import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--months', default=3)
args = parser.parse_args()

rolename = "STSAccountAccess"
# datalake accountId

total_months = args.months

reference_filename_without_discount = "cost_reference_without_discount.csv"
challenger_filename_without_discount = "cost_challenger_without_discount.csv"
reference_filename_with_discount = "cost_reference_with_discount.csv"
challenger_filename_with_discount = "cost_challenger_with_discount.csv"
challenger_filename_before = "cost_challenger_before.csv"
output_filename = "discrepancy_file.csv"
