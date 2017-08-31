#!/usr/bin/python

import os
from os import path
import sys
import argparse
import numpy as np
from subprocess import check_call, check_output, Popen, PIPE

import project_root
from analysis.tunnel_graph import TunnelGraph
from helpers.helpers import make_sure_path_exists, parse_config


def stop_condition(scores):
    max_idx = scores.index(max(scores))
    length = len(scores)

    if length > max_idx + 3:
        return True
    else:
        return False


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
            '--rlcc-dir', default='/home/francis/RLCC',
            help='RLCC path to create traces (default: /home/francis/RLCC)')
    parser.add_argument(
            '--pantheon-dir', default='/home/francis/pantheon',
            help='path to pantheon/ (default: /home/francis/pantheon)')
    parser.add_argument(
            '--trace-folder', default='/home/francis/pantheon/test',
            help='path to bandwidth traces (default: /home/francis/pantheon/test)')
    parser.add_argument(
            "--bandwidths", metavar='"BW1 BW2..."', help="(link rates)")
    parser.add_argument(
            "--delays", metavar='"DELAY1 DELAY2..."',
            help="one way propagation delays in ms")
    parser.add_argument(
            "--cwnd-guess", metavar='PATH',
            default='/home/francis/pantheon/test/cwnd-guess',
            help='default /home/francis/pantheon/test/cwnd-guess')

    args = parser.parse_args()

    make_sure_path_exists(args.cwnd_guess)

    # generate traces
    bandwidths = args.bandwidths.split()
    for bandwidth in bandwidths:
        check_call('%s/helpers/generate_trace.py --bandwidth %s --output-dir %s'
                    % (args.rlcc_dir, bandwidth, args.trace_folder), shell=True)

    history_path = path.join(args.cwnd_guess, 'history')
    history = open(history_path, 'a', 1)

    # for each combination of bandwidth & trace & scheme, run a test
    for bandwidth in bandwidths:
        for delay in args.delays.split():
            cwnd = 2 * int(delay) * int(bandwidth) / 12.0
            cwnd = 10 * int(cwnd / 10.0) - 20
            if cwnd < 10:
                cwnd = 10

            scores = []

            while True:
                data_dir = path.join(args.cwnd_guess,
                        '%smbps-%sdelay-%scwnd' % (bandwidth, delay, cwnd))

                check_call('%s/test/test.py local --schemes rlcc '
                           '--data-dir %s --pkill-cleanup '
                           '--uplink-trace %s/%smbps.trace '
                           '--downlink-trace %s/%smbps.trace '
                           '--prepend-mm-cmds "mm-delay %s" --cwnd %s'
                           % (args.pantheon_dir, data_dir,
                           args.trace_folder, bandwidth,
                           args.trace_folder, bandwidth,
                           delay, cwnd), shell=True)

                tunnel_graph = TunnelGraph(
                    tunnel_log=path.join(data_dir, 'rlcc_datalink_run1.log'))
                tunnel_results = tunnel_graph.run()

                tput = float(tunnel_results['throughput'])
                perc_delay = float(tunnel_results['delay'])

                util = 100.0 * tput / float(bandwidth)
                score = np.log(util) - np.log(perc_delay)
                scores.append(score)

                history.write('%s %s %s %s %s %s\n' %
                              (bandwidth, delay, cwnd, tput, perc_delay, score))

                bw = int(bandwidth)
                if stop_condition(scores):
                    if bw >= 100:
                        if util >= 95 or perc_delay - float(delay) >= 30:
                            break
                    else:
                        if bw - tput <= 1:
                            break

                if bw >= 500:
                    cwnd += 40
                elif bw >= 200:
                    cwnd += 20
                elif bw >= 10:
                    cwnd += 10
                else:
                    cwnd += 5

    history.close()


if __name__ == '__main__':
    main()
