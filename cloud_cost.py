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

def cloud_cost_queries(account, cloud, month, tagged):
    if tagged:
        if account=="822924222578":
            filters = {
                "And": [{
                    "Dimensions": {
                        "Key": "LINKED_ACCOUNT",
                        "Values": [("%s" % (account))]
                    }
                },
                    {
                        "Not": {
                            'Tags': {
                                'Key': 'fc.cloud.name',
                                'Values': cloud
                            }
                        }
                    }
                ],
            }
        else:
            filters = {
                "And": [{
                    "Dimensions": {
                        "Key": "LINKED_ACCOUNT",
                        "Values": [("%s" % (account))]
                    }
                },
                    {
                        'Tags': {
                            'Key': 'fc.cloud.name',
                            'Values': cloud
                        }
                    }
                ],
            }
        cloud_cost_response = clientce.get_cost_and_usage(
            TimePeriod={
                'Start':("%s" % (gtd.getDate(month)[0])),
                'End': ("%s" % (gtd.getDate(month)[1]))
            },
            Granularity='MONTHLY',
            Metrics=["BlendedCost", "UnblendedCost", "AmortizedCost"],
            Filter = filters
        )
        print(cloud_cost_response)
        csv.write_cost_to_csv(prop.reference_filename_with_discount, cloud_cost_response, account)

    else:
        if account=="822924222578":
            filters = {
                "And": [{
                    "Dimensions": {
                        "Key": "LINKED_ACCOUNT",
                        "Values": [("%s" % (account))]
                    }
                },
                    {
                        "Not":{
                            "Dimensions": {
                                "Key": "RECORD_TYPE",
                                "Values": ["Refund", "Enterprise Discount Program Discount", "Credit"],
                            }
                        }
                    }]
            }
        else:
            filters = {
                "And": [{
                    "Dimensions": {
                        "Key": "LINKED_ACCOUNT",
                        "Values": [("%s" % (account))]
                    }
                },
                    {
                        'Tags': {
                            'Key': 'fc.cloud.name',
                            'Values': cloud
                        }
                    },
                    {
                        "Not": {
                            "Dimensions": {
                                "Key": "RECORD_TYPE",
                                "Values": ["Refund", "Enterprise Discount Program Discount", "Credit"],
                            }
                        }
                    }
                ],
            }
        cloud_cost_response = clientce.get_cost_and_usage(
            TimePeriod={
                'Start':("%s" % (gtd.getDate(month)[0])),
                'End': ("%s" % (gtd.getDate(month)[1]))
            },
            Granularity='MONTHLY',
            Metrics=["BlendedCost", "UnblendedCost", "AmortizedCost"],
            Filter = filters
        )
        print(cloud_cost_response)
        csv.write_cost_to_csv(prop.reference_filename_without_discount, cloud_cost_response, account)

def compare_cloud_cost(discount):

    accounts = prop.account_id
    for i in range(len(accounts)):
        account = accounts[i]
        if account=="504325195528":
            cloud_name = ["", "shared-eu-west-1"]
        elif account=="822924222578":
            cloud_name = ["shared-eu-west-1","performance", "shared-us-east-1", "shared-ap-southeast-1", "beta", "datalake", "fluent-datalake"]
        elif account=="909623503793":
            cloud_name = ["", "performance"]
        elif account=="750569990223":
            cloud_name = ["", "shared-us-east-1"]
        elif account=="701896070655":
            cloud_name = ["", "datalake","fluent-datalake","targ","multi","dublin","jdsuk","wool"]
        elif account=="275165877448":
            cloud_name = ["", "shared-ap-southeast-1"]
        elif account=="311047595470":
            cloud_name = ["", "beta"]
        for i in range(int(prop.total_months)):
            month = i + 1
            if discount:
                comparison_name = f"cloud cost for {account} - month {month}. discount ?: {discount}"
                cloud_cost_queries(account, cloud_name, month, discount)
                get_cloud_cost_challanger(account, cloud_name, month, discount)
            else:
                comparison_name = f"cloud cost for {account} - month {month}. discount ?: {discount}"
                cloud_cost_queries(account, cloud_name, month, discount)
                get_cloud_cost_challanger(account, cloud_name, month, discount)
    result_wd = csv.compareCsvFiles(prop.reference_filename_without_discount, prop.challenger_filename_without_discount, prop.output_filename, comparison_name)
    return result_wd

def get_cloud_cost_challanger(account, cloud_names, month, discount):
    if discount:
        query = acq.cloud_cost_with_discount(month, account, cloud_names)
        execute_get_cost_challanger(query, account, prop.challenger_filename_before, prop.challenger_filename_with_discount, prop.rolename, prop.accountId)
    else:
        query = acq.cloud_cost_without_discount(month, account, cloud_names)
        execute_get_cost_challanger(query, account, prop.challenger_filename_before, prop.challenger_filename_without_discount, prop.rolename, prop.accountId)

def execute_get_cost_challanger(query, account, challenger_filename_before, challenger_filename, rolename, accountId):
    aqe.athena_to_s3(sts, acq.params, query, challenger_filename_before, rolename, accountId)
    csv.roundCsvValues(prop.challenger_filename_before, account, challenger_filename)

def cloud_cost_comparison():
    print("Cloud cost comparison has started successfully")
    csv.createAndWriteCsvHeader(prop.csv_list_header)
    result_live = compare_cloud_cost(True)
    result_non_live = compare_cloud_cost(False)
    if result_live=="Failed" or result_non_live=="Failed":
        raise AssertionError("Tenant Cost Comparison: Failed")
    else:
        print("All the cloud cost comparison for has successfully finished")

current_dir = util.switch_workspace('Cloud')
cloud_cost_comparison()
util.switch_back(current_dir)