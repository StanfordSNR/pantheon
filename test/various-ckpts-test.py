#!/usr/bin/env python

import sys
import argparse
import copy
import json
from os import path
from subprocess import check_call
import project_root
from helpers.helpers import parse_config

schemes_ckpts = {
        'indigo': [-1],
        'indigo-2-128': [-1, 120],
        'indigo-2-64': [-1, 130, 120, 110, 100, 90, 80, 70, 60, 50, 40, 30, 20, 10],
        'indigo-2-32': [-1, 120, 110, 100, 90, 80, 70, 60, 50, 40, 30, 20, 10],
        'indigo-2-16': [-1, 130, 120, 110, 100, 90, 80, 70, 60, 50, 40, 30, 20, 10],
        'indigo-2-8': [-1],
        'indigo-2-4': [-1, 110, 100, 90, 80, 70, 60, 50, 40, 30, 20, 10],
        'indigo-1-256': [-1, 120],#], 80],
        'indigo-1-128': [-1, 130, 120, 110, 100, 90, 80, 70, 60, 50, 40, 30, 20, 10],
        'indigo-1-64': [110],#-1, 120, 110, 100, 90, 80, 70, 60, 50, 40, 30, 20, 10],
        'indigo-1-32': [-1, 130, 120, 110, 100, 90, 80, 70, 60, 50, 40, 30, 20, 10],
        'indigo-1-16': [-1, 130, 120, 110, 100, 90, 80, 70, 60, 50, 40, 30, 20, 10],
        'indigo-1-8': [40],#-1, 90, 80, 70, 60, 50, 40, 30, 20, 10],
        'indigo-1-4': [-1, 130, 120, 110, 100, 90, 80, 70, 60, 50, 40, 30, 20, 10],
        'indigo-1-2': [-1, 130, 120, 110, 100, 90, 80, 70, 60, 50, 40, 30, 20, 10],
        'indigo-1-1': [-1, 130, 120, 110, 100, 90, 80, 70, 60, 50, 40, 30, 20, 10],
        }

def get_next_checkpoint(schemes):
    if not hasattr(get_next_checkpoint, "ckpts"):
        get_next_checkpoint.ckpts = copy.deepcopy(schemes_ckpts)

    checkpoints = []
    num_done = 0
    for cc in schemes:
        if cc not in get_next_checkpoint.ckpts:
            get_next_checkpoint.ckpts[cc] = []
            checkpoints.append('-1')
        elif not get_next_checkpoint.ckpts[cc]:
            num_done += 1
            checkpoints.append('-1')
        else:
            checkpoints.append(str(get_next_checkpoint.ckpts[cc].pop()))

    return ' '.join(checkpoints) if num_done != len(schemes) else None


def filter_schemes(schemes):
    all_schemes = parse_config()['schemes']
    valid_schemes = [scheme for scheme in schemes if scheme in all_schemes]
    valid_schemes_str = ' '.join(valid_schemes)
    return valid_schemes, valid_schemes_str


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--schemes', metavar='"SCHEME1 SCHEME2..."', required=True)
    parser.add_argument(
        '--bandwidths', metavar='"BW1 BW2..."', required=True)
    parser.add_argument(
        '--delays', metavar='"DELAY1 DELAY2..."', required=True)
    parser.add_argument('--output-dir', metavar='DIR', required=True)

    args = parser.parse_args()

    schemes = args.schemes.split()
    valid_schemes, valid_schemes_str = filter_schemes(schemes)

    range_test_dir = path.join(project_root.DIR, 'test')
    range_test_src = path.join(range_test_dir, 'range_test.py')

    schemes_stats_dir = path.join(project_root.DIR, 'test')
    schemes_stats_src = path.join(schemes_stats_dir, 'scheme_stats.py')

    # Keep running tests until all checkpoints have been tested.
    while True:
        valid_checkpoints_str = get_next_checkpoint(valid_schemes)
        if valid_checkpoints_str == None:
            print 'Done with all checkpoints'
            break

        print 'Checkpoints: %s' % valid_checkpoints_str

        cmd = ['python', range_test_src,
               '--checkpoints', valid_checkpoints_str,
               '--schemes', valid_schemes_str,
               '--output-dir', args.output_dir,
               '--bandwidths', args.bandwidths,
               '--delays', args.delays]
        sys.stderr.write('$ %s\n' % ' '.join(cmd))
        check_call(cmd)

        cmd = ['python', schemes_stats_src,
               '--schemes', valid_schemes_str,
               '--checkpoints', valid_checkpoints_str,
               '--data-dir', args.output_dir,
               '--bandwidths', args.bandwidths,
               '--delays', args.delays]
        sys.stderr.write('$ %s\n' % ' '.join(cmd))
        check_call(cmd)

    # Combine all jsons into one json.
    all_stats = {}
    for scheme in valid_schemes:
        for ckpt in schemes_ckpts[scheme]:
            cc_ckpt_name = scheme
            if ckpt != -1:
                cc_ckpt_name += '-cp%s' % ckpt

            print 'adding json of %s' % cc_ckpt_name

            stats_json_file = path.join(args.output_dir,
                                        '%s.json' % cc_ckpt_name)
            with open(stats_json_file, 'r') as stats_file:
                cc_ckpt_data = json.load(stats_file)
            all_stats[cc_ckpt_name] = cc_ckpt_data

    all_stats_json_file = path.join(args.output_dir, 'perf_data.json')
    with open(all_stats_json_file, 'w') as f:
        json.dump(all_stats, f)


if __name__ == '__main__':
    main()
