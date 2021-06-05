import re
import csv
import sys
import tempfile
import boto3
import constants.util as util
import constants.properties as prop
import constants.get_date_time as gtd
import athena.athena_cost_queries as acq
import athena.athena_query_execution as aqe

clientce = boto3.client('ce')
sts = boto3.client('sts')

def get_challenger_costs(sts, rolename, account_id, month, file, with_discounts=False):
    costs_by_accounts = {}
    with tempfile.NamedTemporaryFile() as temporary_file:
        athena_query_results_file_name = temporary_file.name
        athena_query = acq.account_costs_without_discounts(month)
        if with_discounts:
            athena_query = acq.account_costs_with_discounts(month)

        aqe.athena_to_s3(sts, acq.params, athena_query, athena_query_results_file_name, rolename, account_id)
        with open(file, 'a+') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')

            with open(athena_query_results_file_name) as f:
                reader = csv.reader(f, delimiter=',', skipinitialspace=True, doublequote=True)
                next(reader, None)
                for row in reader:
                    # extract account id, ex: Shared Dublin 2 (504325195528)
                    account_id = re.findall('[0-9]{5,}', row[0])[0]
                    blended_cost = util.roundoff(row[1])
                    unblended_cost = util.roundoff(row[2])
                    amortized_cost = util.roundoff(row[3])
                    costs_by_accounts[account_id] = {
                        'blended': blended_cost,
                        'unblended': unblended_cost,
                        'amortized': amortized_cost
                    }
                    writer.writerow(
                        [gtd.getDate(month)[0], account_id, blended_cost, unblended_cost, amortized_cost])
    return costs_by_accounts

class AccountCost:

    def __init__(self, cost_explorer_client, sts, total_months):
        self.sts = sts
        self.total_months = total_months
        self.cost_explorer_client = cost_explorer_client
        self.__prepare_csv_files()

    def __prepare_csv_files(self):
        for file in [prop.reference_filename_with_discount, prop.reference_filename_without_discount,
                     prop.challenger_filename_with_discount, prop.challenger_filename_without_discount]:
            self.__write_header(file, "billing_month", "account", "blended_cost", "unblended_cost", "amortized_cost")
        # discrepancy file header
        self.__write_header(prop.output_filename, "billing_month", "account", "reference_blended_cost",
                            "challenger_blended_cost", "reference_unblended_cost", "challenger_unblended_cost",
                            "reference_amortized_cost", "challenger_amortized_cost")

    @staticmethod
    def __write_header(filename, *args):
        with open(filename, 'a+') as csv_file:
            writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_NONE, escapechar=',', doublequote=True)
            writer.writerow(args)

    @staticmethod
    def __compare_and_save_to_disk(reference_costs, challenger_costs, month, discrepancy_output_file):
        all_match = True
        billing_month = gtd.getDate(month)[0]
        with open(discrepancy_output_file, 'a+') as csv_file:
            writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_NONE, escapechar=',', doublequote=True)

            # fail if the number of entries is different
            if not len(challenger_costs) == len(reference_costs):
                writer.writerow([billing_month, 'number of rows in reference and challenger does not match'])
                # exit immediately without comparing any value
                return False
            for account_id in reference_costs:
                reference = reference_costs[account_id]
                challenger = challenger_costs[account_id]
                if (reference['blended'] == challenger['blended']
                        and reference['unblended'] == challenger['unblended']
                        and reference['amortized'] == challenger['amortized']):
                    print('all values match for account: ', account_id)
                else:
                    print('Reference and challenger values are different for account:', account_id, ', reference: ',
                          reference, 'challenger: ', challenger)
                    writer.writerow([billing_month, account_id,
                                     reference['blended'], challenger['blended'],
                                     reference['unblended'], challenger['unblended'],
                                     reference['amortized'], challenger['amortized']])
                    all_match = False
        return all_match

    def compare_account_level_costs(self, with_discounts=False):
        if with_discounts:
            comparison_name = "Account level costs with discounts"
        else:
            comparison_name = "Account level costs without discounts"

        for i in range(self.total_months):
            month = i + 1
            try:
                print('Running Account Level Cost Comparison for month', month, ', include discounts?', with_discounts)

                if with_discounts:
                    reference_costs = self.get_reference_costs(
                        self.cost_explorer_client, month, prop.reference_filename_with_discount, True)
                    challenger_costs = get_challenger_costs(self.sts,
                                                            prop.rolename, prop.accountId, month,
                                                            prop.challenger_filename_with_discount, True)
                else:
                    reference_costs = self.get_reference_costs(
                        self.cost_explorer_client, month, prop.reference_filename_without_discount, False)
                    challenger_costs = get_challenger_costs(self.sts,
                                                            prop.rolename, prop.accountId, month,
                                                            prop.challenger_filename_without_discount, False)

                if not self.__compare_and_save_to_disk(reference_costs, challenger_costs, month, prop.output_filename):
                    raise AssertionError(
                        'Assertion Failure: Account Level reference costs and challenger cost do not match ',
                        'With discounts:', with_discounts, 'reference:', reference_costs, 'challenger:',
                        challenger_costs)
            except:
                e = sys.exc_info()[0]
                print(comparison_name, ' failed with an exception', e)
                raise
        else:
            return "Account Cost Comparison Successful.. "

    @staticmethod
    def get_reference_costs(client, month, file, with_discounts):

        def write_to_disk(cost_response, billing_month, file):
            reference_costs_by_account = {}
            with open(file, 'a+') as csv_file:
                writer = csv.writer(csv_file, delimiter=',')
                for account_cost in cost_response['ResultsByTime'][0]['Groups']:
                    account_id = account_cost['Keys'][0]
                    unblended_cost = util.roundoff(account_cost['Metrics']['UnblendedCost']['Amount'])
                    blended_cost = util.roundoff(account_cost['Metrics']['BlendedCost']['Amount'])
                    amortized_cost = util.roundoff(account_cost['Metrics']['AmortizedCost']['Amount'])
                    reference_costs_by_account[account_id] = {
                        'unblended': unblended_cost,
                        'blended': blended_cost,
                        'amortized': amortized_cost
                    }
                    writer.writerow([billing_month, account_id, blended_cost, unblended_cost, amortized_cost])
            return reference_costs_by_account

        if with_discounts:
            response = client.get_cost_and_usage(
                TimePeriod={
                    'Start': ("%s" % (gtd.getDate(month)[0])),
                    'End': ("%s" % (gtd.getDate(month)[1]))
                },
                Granularity='MONTHLY',
                Metrics=["BlendedCost", "UnblendedCost", "AmortizedCost"],
                GroupBy=[{'Type': 'DIMENSION', 'Key': 'LINKED_ACCOUNT'}]
            )
        else:
            response = client.get_cost_and_usage(
                TimePeriod={
                    'Start': ("%s" % (gtd.getDate(month)[0])),
                    'End': ("%s" % (gtd.getDate(month)[1]))
                },
                Granularity='MONTHLY',
                Metrics=["BlendedCost", "UnblendedCost", "AmortizedCost"],
                GroupBy=[{'Type': 'DIMENSION', 'Key': 'LINKED_ACCOUNT'}],
                Filter={
                    "Not": {
                        "Dimensions": {
                            "Key": "RECORD_TYPE",
                            "Values": ["Refund", "Enterprise Discount Program Discount", "Credit"],
                        }
                    }
                }
            )
        return write_to_disk(response, gtd.getDate(month)[0], file)

current_dir = util.switch_workspace('Account')
account_cost_calculation = AccountCost(clientce, sts, int(prop.total_months))
account_cost_calculation.compare_account_level_costs(False)
account_cost_calculation.compare_account_level_costs(True)
util.switch_back(current_dir)
