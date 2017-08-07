#!/usr/bin/python

import matplotlib
matplotlib.use('Agg')

import project_root
import argparse
import os
import signal
import matplotlib.pyplot as plt
from subprocess import check_call, check_output, Popen, PIPE
from helpers.helpers import make_sure_path_exists


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
    plt.savefig('%smbps-%sdelay/cwnd.png' % (bandwidth, delay))
    plt.clf()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
            '--rlcc-dir', default='/home/jestinm/RLCC',
            help='path to RLCC/ (default: /home/jestinm/RLCC)')
    parser.add_argument(
            '--pantheon-dir', default='/home/jestinm/pantheon',
            help='path to pantheon/ (default: /home/jestinm/pantheon)')
    parser.add_argument(
            '--trace-folder', default='/tmp/traces',
            help='path to bandwidth traces (default: /tmp/traces)')
    parser.add_argument(
            "--delays",
            help="one way propagation delays in ms")
    parser.add_argument(
            "--bandwidths",
            help="(link rates)")
    parser.add_argument(
            "--keep-only-report", action='store_false',
            help="keep just pantheon_report.png and cwnd.png (default: True)")

    args = parser.parse_args()

    # Make sure the bandwidth traces exist in trace folder
    make_sure_path_exists(args.trace_folder)

    for bandwidth in args.bandwidths.split():
        check_call('%s/helpers/generate_trace.py --bandwidth %s --output-dir %s'
                    % (args.rlcc_dir, bandwidth, args.trace_folder),
                    shell=True)

    # for each combination of bandwidth & trace, run the RLCC test
    for bandwidth in args.bandwidths.split():
        for delay in args.delays.split():
            check_call('%s/test/test.py local --schemes rlcc '
                       '--data-dir %smbps-%sdelay --pkill-cleanup '
                       '--uplink-trace %s/%smbps.trace '
                       '--downlink-trace %s/%smbps.trace '
                       '--prepend-mm-cmds "mm-delay %s"' % (args.pantheon_dir,
                       bandwidth, delay, args.trace_folder, bandwidth,
                       args.trace_folder, bandwidth, delay), shell=True)

            check_call('%s/analysis/analyze.py --data-dir=%smbps-%sdelay'
                        % (args.pantheon_dir, bandwidth, delay), shell=True)

            if args.keep_only_report:
                check_call('cd %smbps-%sdelay/ && ls | '
                           'grep -v -E "pantheon_report" | '
                           'xargs rm && cd ..' % (bandwidth, delay),
                           shell=True)

            # generate a graph from the /tmp/cwnd_file
            create_cwnd_change_plot(bandwidth, delay)


if __name__ == '__main__':
    main()
