import constants.csvFunctions as csv
import constants.getDateAndTime as gtd

def get_cost_wo_discounts(clientce, filename, month):
    cost_wo_discount_response = clientce.get_cost_and_usage(
        TimePeriod={
        'Start':("%s" % (gtd.getDate(month)[0])),
        'End': ("%s" % (gtd.getDate(month)[1]))
        },
        Granularity='MONTHLY',
        Metrics=["BlendedCost", "UnblendedCost", "AmortizedCost"],
    )
    bl_c = cost_wo_discount_response['ResultsByTime'][0]['Total']['BlendedCost']['Amount']
    ub_c = cost_wo_discount_response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount']
    am_c = cost_wo_discount_response['ResultsByTime'][0]['Total']['AmortizedCost']['Amount']
    blended_cost = round(float(bl_c), 1)
    unblended_cost = round(float(ub_c), 1)
    amortized_cost = round(float(am_c), 1)
    csv.createAndWriteCsv(filename, blended_cost, unblended_cost, amortized_cost)
    return cost_wo_discount_response

def get_cost_with_discounts(clientce, filename, month):
    cost_with_discount_response = clientce.get_cost_and_usage(
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
    bl_c = cost_with_discount_response['ResultsByTime'][0]['Total']['BlendedCost']['Amount']
    ub_c = cost_with_discount_response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount']
    am_c = cost_with_discount_response['ResultsByTime'][0]['Total']['AmortizedCost']['Amount']
    blended_cost = round(float(bl_c), 1)
    unblended_cost = round(float(ub_c), 1)
    amortized_cost = round(float(am_c), 1)
    csv.createAndWriteCsv(filename, blended_cost, unblended_cost, amortized_cost)
    return cost_with_discount_response
