import athena.athena_query_execution as aqe
import constants.get_date_time as gtd
import athena.athena_cost_queries as acq
import constants.csv_functions as csv
import constants.properties as prop
import constants.util as util
import boto3

clientO = boto3.client('organizations')
clientce = boto3.client('ce')
sts = boto3.client('sts')

def organisation_cost_queries(month, with_discount):
    if with_discount:
        organsiation_cost_response = clientce.get_cost_and_usage(
            TimePeriod={
                'Start':("%s" % (gtd.getDate(month)[0])),
                'End': ("%s" % (gtd.getDate(month)[1]))
            },
            Granularity='MONTHLY',
            Metrics=["BlendedCost", "UnblendedCost", "AmortizedCost"],
            Filter = {
                "Not": {
                    "Dimensions": {
                        "Key": "RECORD_TYPE",
                        "Values": ["Refund", "Enterprise Discount Program Discount", "Credit"],
                    }
                }
            }
        )
        csv.write_cost_to_csv(prop.reference_filename_with_discount, organsiation_cost_response)
    else:
        organsiation_cost_response = clientce.get_cost_and_usage(
            TimePeriod={
                'Start':("%s" % (gtd.getDate(month)[0])),
                'End': ("%s" % (gtd.getDate(month)[1]))
            },
            Granularity='MONTHLY',
            Metrics=["BlendedCost", "UnblendedCost", "AmortizedCost"],
        )
        csv.write_cost_to_csv(prop.reference_filename_without_discount, organsiation_cost_response)

def execute_get_cost_challanger(query, challenger_filename_before, challenger_filename, rolename, accountId):
    aqe.athena_to_s3(sts, acq.params, query, challenger_filename_before, rolename, accountId)
    csv.roundCsvValues(prop.challenger_filename_before, "", challenger_filename)

def get_organisation_cost_challanger(month, with_discount):
    if with_discount:
        query = acq.ath_query_with_discounts(month)
        execute_get_cost_challanger(query, prop.challenger_filename_before, prop.challenger_filename_with_discount, prop.rolename, prop.accountId)
    else:
        query = acq.ath_query_wo_discounts(month)
        execute_get_cost_challanger(query, prop.challenger_filename_before, prop.challenger_filename_without_discount, prop.rolename, prop.accountId)

def compare_organisation_cost(with_discount):
    for i in range(int(prop.total_months)):
        month = i + 1
        if with_discount:
            comparison_name = f"organisation cost - month {month}. discount ?: {with_discount}"
            organisation_cost_queries(month, with_discount)
            get_organisation_cost_challanger(month, with_discount)
            ref_filename = prop.reference_filename_with_discount
            chal_filename = prop.challenger_filename_with_discount
        else:
            comparison_name = f"organisation cost - month {month}. discount ?: {with_discount}"
            organisation_cost_queries(month, with_discount)
            get_organisation_cost_challanger(month, with_discount)
            ref_filename = prop.reference_filename_without_discount
            chal_filename = prop.challenger_filename_without_discount
    result_wd = csv.compareCsvFiles(ref_filename, chal_filename, prop.output_filename, comparison_name)
    return result_wd

def org_cost_comparison():
    print("Organisation cost comparison has started successfully")
    csv.createAndWriteCsvHeader(prop.csv_list_header)
    resultwd = compare_organisation_cost(False)
    resultwod = compare_organisation_cost(True)
    if resultwd=="Failed" or resultwod=="Failed":
        raise AssertionError("Cost Comparison:", resultwd)
    else:
        print("All the organisation cost comparison has successfully finished")

current_dir = util.switch_workspace('Organization')
org_cost_comparison()
util.switch_back(current_dir)