import csv
import pandas as pd
import os.path

def clearCsv(csv_list_clear):
    for i in range(len(csv_list_clear)):
        if os.path.isfile(csv_list_clear[i]):
            f = open(csv_list_clear[i], 'r+')
            f.truncate(0)
            print (csv_list_clear[i] + ": File is already exist and datas have been cleared for new results")
        else:
            print (csv_list_clear[i] + ": File does not exist so new csv file will be created")


def createAndWriteCsvHeader(csv_list_header):
    for i in range(len(csv_list_header)):
        with open(csv_list_header[i], 'a+') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',')
            filewriter.writerow(["billing_from_date", "blended_cost", "unblended_cost", "amortized_cost", "account_id", "region", "environment"])

def createAndWriteCsv(filename, date, blended_cost, unblended_cost, amortized_cost):
    with open(filename, 'a+') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',')
        filewriter.writerow([date, blended_cost, unblended_cost, amortized_cost])

def compareCsvFiles(reference_filename, challenger_filename, output_filename, comparison_name):
    # roundCsvValues(challenger_filename_before, challenger_filename, output_filename)
    with open(reference_filename, 'r') as t1, open(challenger_filename, 'r') as t2:
        source_file = csv.reader(t1, skipinitialspace=True, doublequote=True)
        destination_file = csv.reader(t2, skipinitialspace=True, doublequote=True)
        with open(output_filename, 'a+') as outFile:
            filewriterOut = csv.writer(outFile, delimiter=',', quoting=csv.QUOTE_NONE, escapechar=',', doublequote=True)
            for line in destination_file:
                if line in source_file:
                    status = "Successful"
                    description = (": CSV comparison is successful for " + comparison_name)
                else:
                    status = "Failed"
                    description = (": CSV comparison is not successful for " + comparison_name + ". Please check the " + output_filename + " for the discrepancies")
                    filewriterOut.writerow([comparison_name, status])
                    filewriterOut.writerow(line)
            print(status + description)
    return status

def try_cutoff(x):
    try:
        return round(float(x), 1)
    except Exception:
        return x


def roundCsvValues(challenger_filename_before, challenger_filename):
    col_names = ['billing_from_date',
             'blended_cost',
             'unblended_cost',
             'amortized_cost'
             ]
    dataset = pd.read_csv(challenger_filename_before, names=col_names, skiprows=1)
    for field in dataset.columns:
        dataset[field] = dataset[field].map(try_cutoff)
    dataset.to_csv(challenger_filename, header=None, mode = 'a', index = False)


def write_cost_to_csv(cost_response, filename):
    date = cost_response['ResultsByTime'][0]['TimePeriod']['Start']
    bl_c = cost_response['ResultsByTime'][0]['Total']['BlendedCost']['Amount']
    ub_c = cost_response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount']
    am_c = cost_response['ResultsByTime'][0]['Total']['AmortizedCost']['Amount']
    blended_cost = round(float(bl_c), 1)
    unblended_cost = round(float(ub_c), 1)
    amortized_cost = round(float(am_c), 1)
    createAndWriteCsv(filename, date, blended_cost, unblended_cost, amortized_cost)