import constants.getDateAndTime as gtd

params = {
    'region': 'ap-southeast-2',
    'database': 'default',
    'bucket': 'sathish-bucket',
    'path': 'results/path',
    }
def ath_query_wo_discounts(month):
    query_wo_discounts = ("SELECT SUM(blended_cost) as blended_cost, SUM(unblended_cost) as unblended_cost, SUM(amortised_cost) as amortized_cost \
    FROM aws_costs_view WHERE \
    bill_billing_period_start_date >= from_iso8601_timestamp('%sT00:00:00.000Z') \
    AND \
    bill_billing_period_end_date <= from_iso8601_timestamp('%sT00:00:00.000Z');" % ((gtd.getDate(month)[0]), (gtd.getDate(month)[1])))
    return query_wo_discounts

def ath_query_with_discounts(month):
    query_with_discounts = ("SELECT SUM(blended_cost) as blended_cost, SUM(unblended_cost) as unblended_cost, SUM(amortised_cost) as amortized_cost \
    FROM aws_costs_view WHERE \
    line_item_line_item_type not in ('Refund', 'EdpDiscount', 'Credit') \
    AND \
    bill_billing_period_start_date >= from_iso8601_timestamp('%sT00:00:00.000Z') \
    AND \
    bill_billing_period_end_date <= from_iso8601_timestamp('%sT00:00:00.000Z');" % ((gtd.getDate(month)[0]), (gtd.getDate(month)[1])))
    return query_with_discounts
