import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--months', default=3)
args = parser.parse_args()

rolename = "STSAccountAccess"
# datalake accountId
accountId = "237292"

total_months = args.months
account_id =['123749','67689823']
reference_filename_without_discount = "cost_reference_without_discount.csv"
challenger_filename_without_discount = "cost_challenger_without_discount.csv"
reference_filename_with_discount = "cost_reference_with_discount.csv"
challenger_filename_with_discount = "cost_challenger_with_discount.csv"
challenger_filename_before = "cost_challenger_before.csv"
output_filename = "discrepancy_file.csv"

csv_list_header = [reference_filename_without_discount, reference_filename_with_discount, challenger_filename_with_discount, challenger_filename_without_discount, output_filename]
csv_header = ["billing_from_date", "blended_cost", "unblended_cost", "amortized_cost", "account_id", "service"]
