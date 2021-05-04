import athena.athenaQueryExecution as aqe
import athena.athenaCostQueries as acq

def get_cost_wo_discounts(sts, challenger_filename_before, month, rolename, accountId):
    query  = acq.ath_query_wo_discounts(month)
    aqe.athena_to_s3(sts, acq.params, query, challenger_filename_before, rolename, accountId)

def get_cost_with_discounts(sts, challenger_filename_before, month, rolename, accountId):
    query = acq.ath_query_with_discounts(month)
    aqe.athena_to_s3(sts, acq.params, query, challenger_filename_before, rolename, accountId)
