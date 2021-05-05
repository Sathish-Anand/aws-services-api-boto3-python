#!/usr/bin/env python3.7

import boto3
import botocore
import awscost.getOrganisationCostReference as gtocr
import awscost.getOrganisationCostChallenger as gtocc
import constants.csvFunctions as csv
import constants.properties as prop

clientce = boto3.client('ce')
sts = boto3.client('sts')

total_month = int(prop.total_months)
csv_list_clear = [prop.reference_filename_without_discount, prop.reference_filename_with_discount, prop.challenger_filename_before, prop.challenger_filename_with_discount, prop.challenger_filename_without_discount, prop.output_filename]
csv_list_header = [prop.reference_filename_without_discount, prop.reference_filename_with_discount, prop.challenger_filename_with_discount, prop.challenger_filename_without_discount, prop.output_filename]

def compareOrganisationCostWoDiscounts():
    comparison_name = "organisation cost without discount"
    for i in range(total_month):
        month = i + 1
        get_reference_cost_wod = gtocr.get_cost_wo_discounts(clientce, prop.reference_filename_without_discount, month)
        get_challenger_cost_wod = gtocc.get_cost_wo_discounts(sts, prop.challenger_filename_before, month, prop.rolename, prop.accountId)
    result_wd = csv.compareCsvFiles(prop.reference_filename_without_discount, prop.challenger_filename_before, prop.challenger_filename_without_discount, prop.output_filename, comparison_name)
    print(result_wd)
    return result_wd

def compareOrganisationCostWithDiscounts():
    comparison_name = "organisation cost with discount"
    for i in range(total_month):
        month = i + 1
        get_reference_cost_wd = gtocr.get_cost_with_discounts(clientce, prop.reference_filename_with_discount, month)
        get_challenger_cost_wd = gtocc.get_cost_with_discounts(sts, prop.challenger_filename_before, month, prop.rolename, prop.accountId)
    result_wod = csv.compareCsvFiles(prop.reference_filename_with_discount, prop.challenger_filename_before, prop.challenger_filename_with_discount, prop.output_filename, comparison_name)
    print(result_wod)
    return result_wod

def organisation_cost_comparison():
    csv.clearCsv(csv_list_clear)
    csv.createAndWriteCsvHeader(csv_list_header)
    resultwd = compareOrganisationCostWoDiscounts()
    resultwod = compareOrganisationCostWithDiscounts()
    if  "Failed" in resultwd:
        raise AssertionError(resultwd)
    elif "Failed" in resultwod:
        raise AssertionError(resultwod)
    else:
        print("All the cost comparison has successfully finished")
organisation_cost_comparison()
