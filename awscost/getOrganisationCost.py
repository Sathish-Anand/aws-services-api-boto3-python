import athena.athenaQueryExecution as aqe
import constants.getDateAndTime as gtd
import athena.athenaCostQueries as acq
import constants.csvFunctions as csv
import constants.properties as prop

def organisation_cost_queries(clientce, month, with_discount):
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
        csv.write_cost_to_csv(organsiation_cost_response, prop.reference_filename_with_discount)
    else:
        organsiation_cost_response = clientce.get_cost_and_usage(
            TimePeriod={
                'Start':("%s" % (gtd.getDate(month)[0])),
                'End': ("%s" % (gtd.getDate(month)[1]))
            },
            Granularity='MONTHLY',
            Metrics=["BlendedCost", "UnblendedCost", "AmortizedCost"],
        )
        csv.write_cost_to_csv(organsiation_cost_response, prop.reference_filename_without_discount)

def execute_get_cost_challanger(sts, query, challenger_filename_before, challenger_filename, rolename, accountId):
    aqe.athena_to_s3(sts, acq.params, query, challenger_filename_before, rolename, accountId)
    csv.roundCsvValues(prop.challenger_filename_before, challenger_filename)

def get_organisation_cost_challanger(sts, month, with_discount):
    if with_discount:
        query = acq.ath_query_with_discounts(month)
        execute_get_cost_challanger(sts, query, prop.challenger_filename_before, prop.challenger_filename_with_discount, prop.rolename, prop.accountId)
    else:
        query = acq.ath_query_wo_discounts(month)
        execute_get_cost_challanger(sts, query, prop.challenger_filename_before, prop.challenger_filename_without_discount, prop.rolename, prop.accountId)


def compareOrganisationCost(clientce, sts, with_discount):
    for i in range(int(prop.total_months)):
        month = i + 1
        if with_discount:
            comparison_name = "organisation cost with discount"
            organisation_cost_queries(clientce, month, with_discount)
            get_organisation_cost_challanger(sts, month, with_discount)
        else:
            comparison_name = "organisation cost without discount"
            organisation_cost_queries(clientce, month, with_discount)
            get_organisation_cost_challanger(sts, month, with_discount)
    result_wd = csv.compareCsvFiles(prop.reference_filename_without_discount, prop.challenger_filename_without_discount, prop.output_filename, comparison_name)
    return result_wd