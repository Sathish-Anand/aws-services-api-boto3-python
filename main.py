#!/usr/bin/env python3.7

from multiprocessing import Pool
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--months', default=3)
args = parser.parse_args()

month = args.months

processes = ('account_cost.py --months=%s' % (month),
             'organisation_cost.py --months=%s' % (month),
             'cloud_cost.py --months=%s' % (month),
             'environment_cost.py --months=%s' % (month))

def run_process(process):
    os.system('python3 {}'.format(process))

agent=5
pool = Pool(processes=agent)
pool.map(run_process, processes)
