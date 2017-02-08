#!/usr/bin/env python

import sys
import argparse
import json
import glob
from os import path
import subprocess
import pantheon_helpers
from helpers.pantheon_help import (make_sure_path_exists)

parser = argparse.ArgumentParser()
parser.add_argument('data_dir')
parser.add_argument( 'ms_per_bin', type=int)
args = parser.parse_args()

data_dir = path.abspath(args.data_dir)
raw_logs_dir = path.join(data_dir, 'raw_logs')
analyze_dir = path.dirname(__file__)
greg_logs_dir = path.join(data_dir, 'greg_logs')

merge_logs = path.join(analyze_dir, 'greg-raw-merge-logs.py')
bin_logs = path.join(analyze_dir, 'greg-bin-logs.py')

# load pantheon_metadata.json as a dictionary
metadata_fname = path.join(data_dir, 'pantheon_metadata.json')
with open(metadata_fname) as metadata_file:
    metadata_dict = json.load(metadata_file)

run_times = metadata_dict['run_times']
flows = int(metadata_dict['flows'])
runtime = int(metadata_dict['runtime'])
cc_schemes = metadata_dict['cc_schemes'].split()

make_sure_path_exists(path.join(data_dir, greg_logs_dir))
for cc_scheme in cc_schemes:
    for i in range( 1, run_times + 1 ):
        ingress_path = path.join(raw_logs_dir, '%s_datalink_run%d_*.ingress' % ( cc_scheme, i ))
        egress_path = path.join(raw_logs_dir, '%s_datalink_run%d_*.egress' % ( cc_scheme, i ))
        [ingress_log] = glob.glob(ingress_path)
        [egress_log] = glob.glob(egress_path)

        outfile = 'intermediate_log'
        subprocess.call([merge_logs, '-i', ingress_log, '-e', egress_log, '-o', outfile])
        filename = '%s_run%d.binned' % (cc_scheme, i)
        subprocess.call([bin_logs, outfile, path.join(greg_logs_dir, filename), str(args.ms_per_bin)])
