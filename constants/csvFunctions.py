import csv
import math
import pandas as pd
import os.path
import constants.getDateAndTime as gtd

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
            filewriter.writerow(["billing_from_date", "blended_cost", "unblended_cost", "amortized_cost"])

def createAndWriteCsv(filename, date, blended_cost, unblended_cost, amortized_cost):
    with open(filename, 'a+') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',')
        filewriter.writerow([date, blended_cost, unblended_cost, amortized_cost])

def compareCsvFiles(reference_filename, challenger_filename_before, challenger_filename, output_filename, comparison_name):
    # roundCsvValues(challenger_filename_before, challenger_filename, output_filename)
    with open(reference_filename, 'r') as t1, open(challenger_filename, 'r') as t2:
        source_file = csv.reader(t1, skipinitialspace=True, doublequote=True)
        destination_file = csv.reader(t2, skipinitialspace=True, doublequote=True)
        with open(output_filename, 'a+') as outFile:
            filewriterOut = csv.writer(outFile, delimiter=',', quoting=csv.QUOTE_NONE, escapechar=',', doublequote=True)
            for line in source_file:
                if line in destination_file:
                    status = "successful"
                    description = ("CSV comparison is successful for " + comparison_name)
                    # filewriterOut.writerow(["billing_from_date", "comparison name", "status", "result"])
                    # filewriterOut.writerow([gtd.getDate(month)[0], comparison_name, status, "no discrepancy"])
                else:
                    status = "Failed"
                    description = ("CSV comparison is not successful for " + comparison_name + ". Please check the " + output_filename + " for the descrepancies")
                    filewriterOut.writerow([comparison_name, status])
                    filewriterOut.writerow(line)
                    # raise AssertionError(status +": " +description)
    return status, description

def try_cutoff(x):
    try:
        return round(float(x), 1)
    except Exception:
        return x

def roundCsvValues(challenger_filename_before, challenger_filename, output_filename):
    col_names = ['billing_from_date',
             'blended_cost',
             'unblended_cost',
             'amortized_cost'
             ]
    dataset = pd.read_csv(challenger_filename_before, names=col_names, skiprows=1)
    for field in dataset.columns:
        dataset[field] = dataset[field].map(try_cutoff)
    dataset.to_csv(challenger_filename, header=None, mode = 'a', index = False)
