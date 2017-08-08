#!/usr/bin/python

import matplotlib
matplotlib.use('Agg')

import project_root
import argparse
import sys
import os
import signal
import matplotlib.pyplot as plt
from subprocess import check_call, check_output, Popen, PIPE
from helpers.helpers import make_sure_path_exists, parse_config


def create_cwnd_change_plot(bandwidth, delay):
    cwnd_file = open('/tmp/cwnd_file')
    time_sec = []
    curr_sec = 0
    cwnds = []

    while True:
        line = cwnd_file.readline()
        if not line:
            break

        if len(line) == 0:
            continue

        cwnd = float(line.split()[0])
        cwnds.append(cwnd)
        time_sec.append(curr_sec)
        curr_sec += 0.01

    cwnd_file.close()

    plt.plot(time_sec, cwnds, 'r-')
    plt.xlabel('time (seconds)', fontsize=18)
    plt.ylabel('cwnd size (packets)', fontsize=18)
    plt.savefig('%smbps-%sdelay/cwnd.png' % (bandwidth, delay))
    plt.clf()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
            '--schemes', default='rlcc', metavar='"SCHEME1 SCHEME2..."',
            help='schemes to run (default: rlcc)')
    parser.add_argument(
            '--rlcc-dir', default='/home/jestinm/RLCC',
            help='RLCC path to create traces (default: /home/jestinm/RLCC)')
    parser.add_argument(
            '--pantheon-dir', default='/home/jestinm/pantheon',
            help='path to pantheon/ (default: /home/jestinm/pantheon)')
    parser.add_argument(
            '--trace-folder', default='/tmp/traces',
            help='path to bandwidth traces (default: /tmp/traces)')
    parser.add_argument(
            "--delays", metavar='"DELAY1 DELAY2..."',
            help="one way propagation delays in ms")
    parser.add_argument(
            "--bandwidths", metavar='"BW1 BW2..."',
            help="(link rates)")
    parser.add_argument(
            "--keep-analysis", action='store_true',
            help="keep all output of analysis.py not just pantheon_report.pdf "
                 "(default: False)")

    args = parser.parse_args()

    # Make sure the bandwidth traces exist in trace folder
    make_sure_path_exists(args.trace_folder)

    for bandwidth in args.bandwidths.split():
        check_call('%s/helpers/generate_trace.py --bandwidth %s --output-dir %s'
                    % (args.rlcc_dir, bandwidth, args.trace_folder),
                    shell=True)

    # filter out invalid schemes
    all_schemes = parse_config()['schemes']
    schemes = args.schemes.split()
    valid_schemes = [scheme for scheme in schemes if scheme in all_schemes]
    valid_schemes_str = ' '.join(valid_schemes)

    # for each combination of bandwidth & trace & scheme, run a test
    for bandwidth in args.bandwidths.split():
        for delay in args.delays.split():
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

            if not args.keep_analysis:
                check_call('cd %smbps-%sdelay/ && ls | '
                           'grep -v -E "pantheon_report" | '
                           'xargs rm && cd ..' % (bandwidth, delay),
                           shell=True)

            # for RLCC, generate a graph from the /tmp/cwnd_file
            if 'rlcc' in valid_schemes and os.path.isfile('/tmp/cwnd_file'):
                create_cwnd_change_plot(bandwidth, delay)


if __name__ == '__main__':
    main()
