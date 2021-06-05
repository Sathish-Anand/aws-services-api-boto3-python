import stsaccount.change_sts_account as stsa
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

def environment_cost_queries(account, month, tagged):
    print("Cost Explorer query...")
    if tagged:
        environment_cost_response = clientce.get_cost_and_usage(
            TimePeriod={
                'Start':("%s" % (gtd.getDate(month)[0])),
                'End': ("%s" % (gtd.getDate(month)[1]))
            },
            Granularity='MONTHLY',
            Metrics=["BlendedCost", "UnblendedCost", "AmortizedCost"],
            Filter = {
                "And": [{
                    "Dimensions": {
                        "Key": "LINKED_ACCOUNT",
                        "Values": [("%s" % (account))]
                    }
                },
                    {
                        "Not": {
                            'Tags': {
                                'Key': 'fc.env.type',
                                'Values': [
                                    "ci","common","dedicated","dev", "dev3", "dev4", "engineering", "internal", "operations", "prod", "shared", "testtest", "test2","wow"
                                ]
                            }
                        }
                    }
                ],
            }
        )
        print(environment_cost_response)
        csv.write_cost_to_csv(prop.reference_filename_with_discount, environment_cost_response, account=account)

    else:
        environment_cost_response = clientce.get_cost_and_usage(
            TimePeriod={
                'Start':("%s" % (gtd.getDate(month)[0])),
                'End': ("%s" % (gtd.getDate(month)[1]))
            },
            Granularity='MONTHLY',
            Metrics=["BlendedCost", "UnblendedCost", "AmortizedCost"],
            Filter = {
                "And": [{
                    "Dimensions": {
                        "Key": "LINKED_ACCOUNT",
                        "Values": [("%s" % (account))]
                    },
                },{
                    'Tags': {
                        'Key': 'fc.env.type',
                        'Values': [
                            "ci","common","dedicated","dev", "dev3", "dev4", "engineering", "internal", "operations", "prod", "shared", "testtest", "test2"
                        ]
                    }
                }

                ],
            },
        )
        print(environment_cost_response)
        csv.write_cost_to_csv(prop.reference_filename_without_discount, environment_cost_response, account=account)

def get_environment_cost_challanger(account, month, live_cost):
    if live_cost:
        query = acq.environment_cost_live(month, account)
        execute_get_cost_challanger(query, account, prop.challenger_filename_before, prop.challenger_filename_with_discount, prop.rolename, prop.accountId)
    else:
        query = acq.environment_cost_non_live(month, account)
        execute_get_cost_challanger(query, account, prop.challenger_filename_before, prop.challenger_filename_without_discount, prop.rolename, prop.accountId)

def execute_get_cost_challanger( query, account, challenger_filename_before, challenger_filename, rolename, accountId):
    aqe.athena_to_s3(sts, acq.params, query, challenger_filename_before, rolename, accountId)
    csv.roundCsvValues(prop.challenger_filename_before, account, challenger_filename)

def compare_environment_cost(live_cost):
    accounts = stsa.listAccount(clientO)
    # accounts=["822924222578"]
    for i in range(len(accounts)):
        account = accounts[i]
        print("* * * [" + accounts[i] + "] Environment cost comparison * * *")
        for i in range(int(prop.total_months)):
            month = i + 1
            if live_cost:
                print(f"* [{account}] Live - Month {month}")
                comparison_name = f"production sandbox and staging environment cost for {account} - month {month} with live cost: {live_cost}"
                environment_cost_queries(account, month, live_cost)
                get_environment_cost_challanger(account, month, live_cost)
                ref_filename = prop.reference_filename_with_discount
                chal_filename = prop.challenger_filename_with_discount
            else:
                print(f"* [{account}] Non_Live - Month {month}")
                comparison_name = f"non production sandbox environment environment cost for {account} - month {month} with live cost: {live_cost}"
                environment_cost_queries(account, month, live_cost)
                get_environment_cost_challanger(account, month, live_cost)
                ref_filename = prop.reference_filename_without_discount
                chal_filename = prop.challenger_filename_without_discount
    result_wd = csv.compareCsvFiles(ref_filename, chal_filename, prop.output_filename, comparison_name)
    return result_wd

def environment_cost_comparison():
    print("Environment cost comparison has started successfully")
    csv.createAndWriteCsvHeader(prop.csv_list_header)
    result_live = compare_environment_cost(True)
    result_non_live = compare_environment_cost(False)
    if result_live=="Failed" or result_non_live=="Failed":
        raise AssertionError("Cost Comparison: Failed")
    else:
        print("All the environment cost comparison for has successfully finished")

current_dir = util.switch_workspace('Environment')
environment_cost_comparison()
util.switch_back(current_dir)