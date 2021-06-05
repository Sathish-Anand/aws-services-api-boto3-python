from dateutil.relativedelta import relativedelta
from datetime import date, timedelta

def getDate(month):
    start_day_to_get_cost = date.today().replace(day=1) - relativedelta(months=month)
    last_day_to_get_cost = start_day_to_get_cost + relativedelta(months=1)
    # print ("Get aws cost from :%s till:%s" % (start_day_to_get_cost, last_day_to_get_cost))
    return start_day_to_get_cost, last_day_to_get_cost
