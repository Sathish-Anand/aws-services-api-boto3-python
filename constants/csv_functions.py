import csv
import pandas as pd
import os.path
import constants.properties as prop
import re

account_regex = re.compile('.*?([0-9]{3,})')


def clearCsv(csv_list_clear):
    for i in range(len(csv_list_clear)):
        if os.path.isfile(csv_list_clear[i]):
            f = open(csv_list_clear[i], 'r+')
            f.truncate(0)
            print(csv_list_clear[i] + ": File is already exist and datas have been cleared for new results")
        else:
            print(csv_list_clear[i] + ": File does not exist so new csv file will be created")


def createAndWriteCsvHeader(csv_list_header):
    for i in range(len(csv_list_header)):
        with open(csv_list_header[i], 'a+') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',')
            filewriter.writerow(prop.csv_header)


def createAndWriteCsv(filename, date, blended_cost, unblended_cost, amortized_cost, account="", service=""):
    with open(filename, 'a+') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',')
        filewriter.writerow([date, blended_cost, unblended_cost, amortized_cost, account, service])


def compareCsvFiles(reference_filename, challenger_filename, output_filename, comparison_name):
    # roundCsvValues(challenger_filename_before, challenger_filename, output_filename)
    with open(reference_filename, 'r') as t1, open(challenger_filename, 'r') as t2:
        source_file = csv.reader(t1, skipinitialspace=True, doublequote=True)
        destination_file = csv.reader(t2, skipinitialspace=True, doublequote=True)
        with open(output_filename, 'a+') as outFile:
            filewriterOut = csv.writer(outFile, delimiter=',', quoting=csv.QUOTE_NONE, escapechar=',', doublequote=True)
            # checking each line from Athena response if it has an entry in CostExplorer output
            status = "Success"
            description = "CSV comparison is successful for " + comparison_name
            for line in destination_file:
                if line not in source_file:
                    status = "Failed"
                    description = "CSV comparison is not successful for " + comparison_name + ".\nPlease check the " + output_filename + " for the discrepancies"
                    filewriterOut.writerow([comparison_name, status])
                    filewriterOut.writerow(line)
                t1.seek(0)
            print(description)
    return status


def try_cutoff(x):
    try:
        return round(float(x), 1)
    except Exception:
        return x


def roundCsvValues(challenger_filename_before, account, challenger_filename):
    dataset = pd.read_csv(challenger_filename_before, names=prop.csv_header, skiprows=1)
    for field in dataset.columns:
        if field == "account_id" and dataset[field].size != 0 and pd.notna(dataset[field][0]):
            dataset[field] = dataset[field].astype("string")
            m = account_regex.match(dataset[field][0])
            # dataset[field] = dataset[field].str.strip('aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ2 ) ) ( (')
            # dataset[field] = dataset[field].str.replace('75165877448','275165877448', regex=False)
            if m is None:
                raise Exception(f"Account ID cannot be translated: {dataset[field][0]}")
            dataset[field] = m.group(1)
        else:
            dataset[field] = dataset[field].map(try_cutoff)

    dataset.to_csv(challenger_filename, header=None, mode='a', index=False)


def write_cost_to_csv(filename, cost_response, account="", service=""):
    date = cost_response['ResultsByTime'][0]['TimePeriod']['Start']
    bl_c = cost_response['ResultsByTime'][0]['Total']['BlendedCost']['Amount']
    ub_c = cost_response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount']
    am_c = cost_response['ResultsByTime'][0]['Total']['AmortizedCost']['Amount']
    blended_cost = round(float(bl_c), 1)
    unblended_cost = round(float(ub_c), 1)
    amortized_cost = round(float(am_c), 1)
    createAndWriteCsv(filename, date, blended_cost, unblended_cost, amortized_cost, account=account, service=service)

