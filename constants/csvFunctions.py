import csv
import pandas as pd
import os.path

def clearCsv(filename):
    if os.path.isfile(filename):
        f = open(filename, 'r+')
        f.truncate(0)
        print ("File exist and datas have been cleared for new results")
    else:
        print ("File not exist so new csv file will be created")

def createAndWriteCsv(filename, blended_cost, unblended_cost, amortized_cost):
    clearCsv(filename)
    with open(filename, 'w') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',')
        filewriter.writerow(["blended_cost", "unblended_cost", "amortized_cost"])
        filewriter.writerow([blended_cost, unblended_cost, amortized_cost])

def compareCsvFiles(reference_filename, challenger_filename_before, challenger_filename, output_filename, comparison_name):
    roundCsvValues(challenger_filename_before, challenger_filename, output_filename, comparison_name)
    with open(reference_filename, 'r') as t1, open(challenger_filename, 'r') as t2:
        source_file = csv.reader(t1, skipinitialspace=True, doublequote=True)
        destination_file = csv.reader(t2, skipinitialspace=True, doublequote=True)
        with open(output_filename, 'w') as outFile:
            filewriterOut = csv.writer(outFile, delimiter=' ', quoting=csv.QUOTE_NONE, escapechar='\\', doublequote=True)
            filewriterOut.writerow(comparison_name)
            for line in destination_file:
                if line in source_file:
                    status = "successful"
                    description = ("CSV comparison is successful for " + comparison_name)
                else:
                    filewriterOut.writerow(line)
                    filewriterOut.writerows(source_file)
                    status = "Failed"
                    description = ("CSV comparison is not successful for " + comparison_name + ". Please check the " + output_filename + " for the descrepancies")
                    raise AssertionError(status +": " +description)
            filewriterOut.writerow(status)
    return status, description

def try_cutoff(x):
    try:
        return round(float(x), 1)
    except Exception:
        return x

def roundCsvValues(challenger_filename_before, challenger_filename, output_filename, comparison_name):
    dataset = pd.read_csv(challenger_filename_before)
    for field in dataset.columns:
        dataset[field] = dataset[field].map(try_cutoff)
    dataset.to_csv(challenger_filename, index = False)
