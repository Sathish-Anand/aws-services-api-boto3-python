import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--months', default=3)
args = parser.parse_args()

rolename = "STSAccountAccess"
# datalake accountId
accountId = "123456784"

total_months = args.months

reference_filename = "cost_reference.csv"
challenger_filename = "cost_challenger.csv"
challenger_filename_before = "cost_challenger_before.csv"
output_filename = "discrepancy_file.csv"
