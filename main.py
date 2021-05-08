#!/usr/bin/env python3.7

import boto3
import awscost.getOrganisationCost as gtoc
import awscost.getTenantCost as gttc
import constants.csvFunctions as csv
import constants.util as util
from awscost.account_cost import AccountCost
import constants.properties as prop
import stsAccount.changeSTSaccount as stsa

clientO = boto3.client('organizations')
clientce = boto3.client('ce')
sts = boto3.client('sts')

csv_list_header = [prop.reference_filename_without_discount, prop.reference_filename_with_discount, prop.challenger_filename_with_discount, prop.challenger_filename_without_discount, prop.output_filename]

def org_cost_comparison():
    csv.createAndWriteCsvHeader(csv_list_header)
    resultwd = gtoc.compareOrganisationCost(clientce, sts, False)
    resultwod = gtoc.compareOrganisationCost(clientce, sts, True)
    if resultwd=="Failed" or resultwod=="Failed":
        raise AssertionError("Cost Comparison:", resultwd)
    else:
        print("All the cost comparison has successfully finished")

current_dir = util.switch_workspace('Organization')
org_cost_comparison()
util.switch_back(current_dir)

