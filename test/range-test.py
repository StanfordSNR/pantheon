#!/usr/bin/python

import matplotlib
matplotlib.use('Agg')

import project_root
import argparse
import sys
import os
from os import path
import signal
import matplotlib.pyplot as plt
from subprocess import check_call, check_output, Popen, PIPE
from helpers.helpers import make_sure_path_exists, parse_config


def create_cwnd_change_plot(bandwidth, delay):
    cwnd_file = open('/tmp/cwnd_file')
    steps = []
    cwnds = []

    while True:
        line = cwnd_file.readline()
        if not line:
            break

        if len(line) == 0:
            continue

        cwnd = float(line.split()[0])
        cwnds.append(cwnd)
        steps.append(len(steps))

    cwnd_file.close()

    plt.figure(figsize=(32, 6))
    plt.plot(steps, cwnds, 'r-')
    plt.xlabel('step num.', fontsize=18)
    plt.ylabel('cwnd size (packets)', fontsize=18)
    plt.title('Cwnd changes for RLCC')
    plt.tight_layout()
    plt.savefig('%smbps-%sdelay/cwnd.png' % (bandwidth, delay))
    plt.clf()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
            '--schemes', default='rlcc', metavar='"SCHEME1 SCHEME2..."',
            help='schemes to run (default: rlcc)')
    parser.add_argument(
            '--rlcc-dir', default='/home/francisyyan/RLCC',
            help='RLCC path to create traces (default: /home/francisyyan/RLCC)')
    parser.add_argument(
            '--pantheon-dir', default='/home/francisyyan/pantheon',
            help='path to pantheon/ (default: /home/francisyyan/pantheon)')
    parser.add_argument(
            '--trace-folder', default='/home/francisyyan/pantheon/test',
            help='path to bandwidth traces (default: /home/francisyyan/pantheon/test)')
    parser.add_argument(
            "--bandwidths", metavar='"BW1 BW2..."',
            help="(link rates)")
    parser.add_argument(
            "--delays", metavar='"DELAY1 DELAY2..."',
            help="one way propagation delays in ms")
    parser.add_argument(
            "--keep-analysis", action='store_true',
            help="keep all output of analysis.py not just pantheon_report.pdf "
                 "(default: False)")
    parser.add_argument(
            "--plot-scores", action='store_true',
            help="plot the link rate scores of all schemes (default: False)")

    args = parser.parse_args()

    # Make sure the bandwidth traces exist in trace folder
    make_sure_path_exists(args.trace_folder)

    bandwidths = args.bandwidths.split()
    assert len(bandwidths) > 0, 'Must have at least one bandwidth to test'

    for bandwidth in bandwidths:
        if not path.isfile('%s/%smbps.trace' % (args.trace_folder, bandwidth)):
            check_call('%s/helpers/generate_trace.py --bandwidth %s --output-dir %s'
                       % (args.rlcc_dir, bandwidth, args.trace_folder), shell=True)

    # filter out invalid schemes
    all_schemes = parse_config()['schemes']
    schemes = args.schemes.split()
    valid_schemes = [scheme for scheme in schemes if scheme in all_schemes]
    valid_schemes_str = ' '.join(valid_schemes)

    # for each combination of bandwidth & trace & scheme, run a test
    for delay in args.delays.split():
        for bandwidth in bandwidths:
            check_call('%s/test/test.py local --schemes "%s" '
                       '--data-dir %smbps-%sdelay --pkill-cleanup '
                       '--uplink-trace %s/%smbps.trace '
                       '--downlink-trace %s/%smbps.trace '
                       '--prepend-mm-cmds "mm-delay %s"'
                       % (args.pantheon_dir, valid_schemes_str,
                       bandwidth, delay, args.trace_folder, bandwidth,
                       args.trace_folder, bandwidth, delay), shell=True)

            check_call('%s/analysis/analyze.py --data-dir=%smbps-%sdelay'
                        % (args.pantheon_dir, bandwidth, delay), shell=True)

            # for RLCC, generate a graph from the /tmp/cwnd_file
            if 'rlcc' in valid_schemes and os.path.isfile('/tmp/cwnd_file'):
                create_cwnd_change_plot(bandwidth, delay)

        # for 1 delay and X bandwidths, generate link score png
        if args.plot_scores:
            check_call('%s/test/plot_linkrate_score.py --data-dir . --delay %s '
                       '--suffix mbps-%sdelay --bandwidths "%s" --schemes "%s"'
                       % (args.pantheon_dir, delay, delay,
                          args.bandwidths, ','.join(valid_schemes)),
                       shell=True)

        # delete files after using them to create link score png
        if not args.keep_analysis:
            for bandwidth in bandwidths:
                check_call('cd %smbps-%sdelay/ && ls | '
                           'grep -v -E "pantheon_report|cwnd|stats_run" | '
                           'xargs rm && cd ..' % (bandwidth, delay),
                           shell=True)


if __name__ == '__main__':
    main()
