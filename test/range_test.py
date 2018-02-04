#!/usr/bin/env python

import sys
import argparse
from os import path
from subprocess import check_call
import project_root
from helpers.helpers import parse_config


def generate_traces(bandwidths, output_dir):
    test_dir = path.join(project_root.DIR, 'test')
    gen_trace = path.join(test_dir, 'generate_trace.py')

    for bw in bandwidths:
        trace_path = path.join(output_dir, '%smbps.trace' % bw)
        if not path.isfile(trace_path):
            cmd = ['python', gen_trace,
                   '--bandwidth', bw, '--output-dir', output_dir]
            sys.stderr.write('$ %s\n' % ' '.join(cmd))
            check_call(cmd)


def filter_schemes(schemes, cps):
    all_schemes = parse_config()['schemes']
    valid_checkpoints = [cps[i] for i in xrange(len(cps)) if schemes[i] in all_schemes]
    valid_schemes = [scheme for scheme in schemes if scheme in all_schemes]

    valid_checkpoints_str = ' '.join(valid_checkpoints)
    valid_schemes_str = ' '.join(valid_schemes)

    return valid_schemes_str, valid_checkpoints_str


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--schemes', metavar='"SCHEME1 SCHEME2..."', required=True)
    parser.add_argument(
        '--checkpoints', metavar='CP1, CP2, CP3',
        help='Number checkpoints for each scheme. Must match schemes in length. Put -1 for none.')
    parser.add_argument(
        '--bandwidths', metavar='"BW1 BW2..."', required=True)
    parser.add_argument(
        '--delays', metavar='"DELAY1 DELAY2..."', required=True)
    parser.add_argument('--output-dir', metavar='DIR', required=True)

    args = parser.parse_args()
    output_dir = args.output_dir

    bandwidths = args.bandwidths.split()
    delays = args.delays.split()
    generate_traces(bandwidths, output_dir)

    schemes = args.schemes.split()
    if args.checkpoints is not None:
        checkpoints = args.checkpoints.split()
    else:
        checkpoints = [-1] * len(schemes)

    assert len(schemes) == len(checkpoints)
    valid_schemes_str, valid_checkpoints_str = filter_schemes(schemes, checkpoints)

    test_dir = path.join(project_root.DIR, 'test')
    test_src = path.join(test_dir, 'test.py')
    plot_src = path.join(project_root.DIR, 'analysis', 'plot.py')

    for bw in bandwidths:
        for delay in delays:
            trace_path = path.join(output_dir, '%smbps.trace' % bw)
            data_dir = path.join(output_dir, '%smbps-%sms' % (bw, delay))

            cmd = ['python', test_src, 'local',
                   '--checkpoints', valid_checkpoints_str,
                   '--schemes', valid_schemes_str,
                   '--data-dir', data_dir,
                   '--uplink-trace', trace_path,
                   '--downlink-trace', trace_path,
                   '--prepend-mm-cmds', 'mm-delay %s' % delay,
                   '--pkill-cleanup']
            sys.stderr.write('$ %s\n' % ' '.join(cmd))
            check_call(cmd)

            cmd = ['python', plot_src, '--schemes', valid_schemes_str,
                   '--data-dir', data_dir, '--no-graphs']
            sys.stderr.write('$ %s\n' % ' '.join(cmd))
            check_call(cmd)


if __name__ == '__main__':
    main()
