import athena.athenaQueryExecution as aqe
import athena.athenaCostQueries as acq
import constants.getDateAndTime as gtd
import constants.csvFunctions as csv
import constants.properties as prop

def get_cost_wo_discounts(sts, challenger_filename_before, month, rolename, accountId):
    query  = acq.ath_query_wo_discounts(month)
    date = gtd.getDate(month)[0]
    aqe.athena_to_s3(sts, acq.params, query, challenger_filename_before, rolename, accountId)
    csv.roundCsvValues(prop.challenger_filename_before, prop.challenger_filename_without_discount, prop.output_filename)
    return date

def get_cost_with_discounts(sts, challenger_filename_before, month, rolename, accountId):
    query = acq.ath_query_with_discounts(month)
    date = gtd.getDate(month)[0]
    aqe.athena_to_s3(sts, acq.params, query, challenger_filename_before, rolename, accountId)
    csv.roundCsvValues(prop.challenger_filename_before, prop.challenger_filename_with_discount, prop.output_filename)
    return date
