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

def compareOrganisationCostWoDiscounts():
    comparison_name = "organisation cost without discount"
    for i in range(total_month):
        month = i + 1
        get_reference_cost_wod = gtocr.get_cost_wo_discounts(clientce, prop.reference_filename, month)
        get_challenger_cost_wod = gtocc.get_cost_wo_discounts(sts, prop.challenger_filename_before, month, prop.rolename, prop.accountId)
        try:
            result = csv.compareCsvFiles(prop.reference_filename, prop.challenger_filename_before, prop.challenger_filename, prop.output_filename, comparison_name)
            print(result)
        except botocore.exceptions.ClientError as e:
            print(comparison_name + " failed with an exception", e)
    else:
        print("All the " + comparison_name + " comparison has successfully finished")
    return result

def compareOrganisationCostWithDiscounts():
    comparison_name = "organisation cost with discount"
    for i in range(total_month):
        month = i + 1
        get_reference_cost_wd = gtocr.get_cost_with_discounts(clientce, prop.reference_filename, month)
        get_challenger_cost_wd = gtocc.get_cost_with_discounts(sts, prop.challenger_filename_before, month, prop.rolename, prop.accountId)
        try:
            result = csv.compareCsvFiles(prop.reference_filename, prop.challenger_filename_before, prop.challenger_filename, prop.output_filename, comparison_name)
            print(result)
        except botocore.exceptions.ClientError as e:
            print(comparison_name + "failed with an exception", e)
    else:
        print("All the " + comparison_name + " comparison has successfully finished")
    return result

def organisation_cost_comparison():
    compareOrganisationCostWoDiscounts()
    compareOrganisationCostWithDiscounts()

organisation_cost_comparison()
