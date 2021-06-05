import constants.get_date_time as gtd
from io import StringIO

params = {
    'region': 'ap-southeast-2',
    'database': 'default',
    'bucket': 'aws-cost-test-datas',
    'path': 'results/tests',
    }

year_format = "%Y-%m-%d"
percent = "%"

class StringBuilder:
    _file_str = None

    def __init__(self):
        self._file_str = StringIO()

    def Append(self, str):
        self._file_str.write(u'%s' %(str))

    def __str__(self):
        return self._file_str.getvalue()

    def Truncate(self,value):
        return self._file_str.truncate(value)

    def Seek(self,value):
        return self._file_str.seek(value)


sb = StringBuilder()

def ath_query_wo_discounts(month):
    query_wo_discounts = ("SELECT date_format(bill_billing_period_start_date,'%s') as billing_from_date, SUM(blended_cost) as blended_cost, SUM(unblended_cost) as unblended_cost, SUM(amortised_cost) as amortized_cost \
    FROM aws_costs_view WHERE \
    bill_billing_period_start_date >= from_iso8601_timestamp('%sT00:00:00.000Z') \
    AND \
    bill_billing_period_end_date <= from_iso8601_timestamp('%sT00:00:00.000Z') Group by 1;" % (year_format, (gtd.getDate(month)[0]), (gtd.getDate(month)[1])))
    return query_wo_discounts


def ath_query_with_discounts(month):
    query_with_discounts = ("SELECT date_format(bill_billing_period_start_date,'%s') as billing_from_date, SUM(blended_cost) as blended_cost, SUM(unblended_cost) as unblended_cost, SUM(amortised_cost) as amortized_cost \
    FROM aws_costs_view WHERE \
    line_item_line_item_type not in ('Refund', 'EdpDiscount', 'Credit') \
    AND \
    bill_billing_period_start_date >= from_iso8601_timestamp('%sT00:00:00.000Z') \
    AND \
    bill_billing_period_end_date <= from_iso8601_timestamp('%sT00:00:00.000Z') Group by 1;" % (year_format, (gtd.getDate(month)[0]), (gtd.getDate(month)[1])))
    return query_with_discounts


def account_costs_with_discounts(month):
    return ("SELECT line_item_usage_account_id as account, SUM(blended_cost) as blended_cost, \
    SUM(unblended_cost) as unblended_cost, SUM(amortised_cost) as amortized_cost \
    FROM aws_costs_view WHERE \
    bill_billing_period_start_date >= from_iso8601_timestamp('%sT00:00:00.000Z') \
    AND \
    bill_billing_period_end_date <= from_iso8601_timestamp('%sT00:00:00.000Z') \
    GROUP BY line_item_usage_account_id   ORDER BY 1;" % ((gtd.getDate(month)[0]), (gtd.getDate(month)[1])))


def account_costs_without_discounts(month):
    return ("SELECT line_item_usage_account_id as account, SUM(blended_cost) as blended_cost, \
    SUM(unblended_cost) as unblended_cost, SUM(amortised_cost) as amortized_cost \
    FROM aws_costs_view WHERE \
    line_item_line_item_type not in ('Refund', 'EdpDiscount', 'Credit') AND \
    bill_billing_period_start_date >= from_iso8601_timestamp('%sT00:00:00.000Z') \
    AND \
    bill_billing_period_end_date <= from_iso8601_timestamp('%sT00:00:00.000Z') \
    GROUP BY line_item_usage_account_id   ORDER BY 1;" % ((gtd.getDate(month)[0]), (gtd.getDate(month)[1])))


def environment_cost_live(month, accounts):
    account = "%"+accounts+"%"
    return ("SELECT date_format(bill_billing_period_start_date,'%s') as billing_from_date,\
    SUM(blended_cost) AS blended_cost, SUM(unblended_cost) AS unblended_cost, SUM(amortised_cost) AS amortized_cost, \
    line_item_usage_account_id as account \
    FROM aws_costs_view \
    WHERE line_item_usage_account_id LIKE '%s' \
    AND resource_tags_user_fc_env_type IN ('production', 'sandbox', 'staging', 'production-sandbox-staging-test','test','ap-southeast-2','eu-west-1','AdrianSpecial') \
    AND bill_billing_period_start_date >= from_iso8601_timestamp('%sT00:00:00.000Z') \
    AND bill_billing_period_end_date <= from_iso8601_timestamp('%sT00:00:00.000Z') \
    GROUP BY  1,5;" % (year_format, account, (gtd.getDate(month)[0]), (gtd.getDate(month)[1])))

def environment_cost_non_live(month, accounts):
    account = "%"+accounts+"%"
    return ("SELECT date_format(bill_billing_period_start_date,'%s') as billing_from_date,\
        SUM(blended_cost) AS blended_cost, SUM(unblended_cost) AS unblended_cost, SUM(amortised_cost) AS amortized_cost, \
        line_item_usage_account_id as account \
        FROM aws_costs_view \
        WHERE line_item_usage_account_id LIKE '%s' \
        AND resource_tags_user_fc_env_type IN ('ci','common','dedicated','dev', 'dev3', 'dev4', 'engineering', 'internal', 'operations', 'prod', 'shared','testtest', 'test2') \
        AND bill_billing_period_start_date >= from_iso8601_timestamp('%sT00:00:00.000Z') \
        AND bill_billing_period_end_date <= from_iso8601_timestamp('%sT00:00:00.000Z') \
        GROUP BY  1,5; " % (year_format, account, (gtd.getDate(month)[0]), (gtd.getDate(month)[1])))

def cloud_cost_without_discount(month, accounts, cloud_name):
    account = "%"+accounts+"%"
    account_like = accounts+"-%"
    sb.Truncate(0)
    sb.Seek(0)
    if accounts=="822924222578":
        for j in range(len(cloud_name)):
            sb.Append("OR resource_tags_user_fc_cloud_name NOT LIKE '%s%s%s' " % (percent,cloud_name[j],percent))
        cloud_names = sb
    else:
        for j in range(len(cloud_name)):
            sb.Append("OR resource_tags_user_fc_cloud_name LIKE '%s%s%s' " % (percent,cloud_name[j],percent))
        cloud_names = sb
    return("SELECT\
    date_format(bill_billing_period_start_date,'%s') as billing_from_date,\
    SUM(blended_cost) AS blended_cost, SUM(unblended_cost) AS unblended_cost, SUM(amortised_cost) AS amortized_cost,\
    line_item_usage_account_id as account\
    FROM aws_costs_view\
    WHERE line_item_usage_account_id LIKE '%s'\
    AND line_item_line_item_type NOT IN ('Refund', 'EdpDiscount', 'Credit')\
    AND bill_billing_period_start_date >= from_iso8601_timestamp('%sT00:00:00.000Z')\
    AND bill_billing_period_end_date <= from_iso8601_timestamp('%sT00:00:00.000Z')\
    AND (resource_tags_user_fc_cloud_name LIKE '%s' %s)\
    GROUP BY  1,5; " % (year_format, account, (gtd.getDate(month)[0]), (gtd.getDate(month)[1]), account_like, cloud_names))

def cloud_cost_with_discount(month, accounts, cloud_name):
    account = "%"+accounts+"%"
    account_like = accounts+"-%"
    sb.Truncate(0)
    sb.Seek(0)
    if accounts=="822924222578":
        for j in range(len(cloud_name)):
            sb.Append("OR resource_tags_user_fc_cloud_name NOT LIKE '%s%s%s' " % (percent,cloud_name[j],percent))
        cloud_names = sb
    else:
        for j in range(len(cloud_name)):
            sb.Append("OR resource_tags_user_fc_cloud_name LIKE '%s%s%s' " % (percent,cloud_name[j],percent))
        cloud_names = sb
    return("SELECT\
    date_format(bill_billing_period_start_date,'%s') as billing_from_date,\
    SUM(blended_cost) AS blended_cost, SUM(unblended_cost) AS unblended_cost, SUM(amortised_cost) AS amortized_cost,\
    line_item_usage_account_id as account\
    FROM aws_costs_view\
    WHERE line_item_usage_account_id LIKE '%s'\
    AND bill_billing_period_start_date >= from_iso8601_timestamp('%sT00:00:00.000Z')\
    AND bill_billing_period_end_date <= from_iso8601_timestamp('%sT00:00:00.000Z') \
    AND (resource_tags_user_fc_cloud_name LIKE '%s' %s)\
    GROUP BY  1,5; " % (year_format, account, (gtd.getDate(month)[0]), (gtd.getDate(month)[1]), account_like, cloud_names))

def service_cost_query(month, accounts):
    account = "%"+accounts+"%"
    return ("SELECT date_format(bill_billing_period_start_date,'%s') as billing_from_date, \
        ROUND(SUM(blended_cost),0) AS blended_cost, ROUND(SUM(unblended_cost),0) AS unblended_cost, ROUND(SUM(amortised_cost),0) AS amortized_cost, \
        line_item_usage_account_id as account, \
        line_item_product_code as service     \
        FROM aws_costs_view \
        WHERE line_item_usage_account_id LIKE '%s' \
        AND bill_billing_period_start_date >= from_iso8601_timestamp('%sT00:00:00.000Z') \
        AND bill_billing_period_end_date <= from_iso8601_timestamp('%sT00:00:00.000Z') \
        AND line_item_line_item_type IN ('Fee', 'Usage', 'DiscountedUsage') \
            GROUP BY 1,5,6;" % (year_format, account, (gtd.getDate(month)[0]), (gtd.getDate(month)[1])))
