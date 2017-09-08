#!/usr/bin/python

import os
from os import path
import shutil
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

    if length > max_idx + 5:
        return True
    else:
        return False


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--rlcc-dir', default='/home/ubuntu/RLCC')
    parser.add_argument('--pantheon-dir', default='/home/ubuntu/pantheon')
    parser.add_argument('--trace-folder', default='/home/ubuntu/pantheon/test')
    parser.add_argument("--cwnd-guess", metavar='PATH',
                        default='/home/ubuntu/pantheon/test/cwnd-guess')

    args = parser.parse_args()

    make_sure_path_exists(args.cwnd_guess)

    history_path = path.join(args.cwnd_guess, 'history')
    history = open(history_path, 'a', 1)

    cwnd = 10
    if cwnd < 5:
        cwnd = 5

    scores = []

    while True:
        data_dir = path.join(args.cwnd_guess, 'cwnd-%d' % cwnd)

        check_call(
            '%s/test/test.py local --schemes rlcc '
            '--data-dir %s --pkill-cleanup '
            '--uplink-trace %s/ '
            '--downlink-trace %s/ '
            '--prepend-mm-cmds "mm-delay " '
            '--cwnd %s'
            % (args.pantheon_dir, data_dir,
            args.trace_folder, args.trace_folder,
            cwnd), shell=True)

        tunnel_graph = TunnelGraph(
            tunnel_log=path.join(data_dir, 'rlcc_datalink_run1.log'))
        tunnel_results = tunnel_graph.run()

        tput = float(tunnel_results['throughput'])
        perc_delay = float(tunnel_results['delay'])

        score = np.log(tput) - np.log(perc_delay)
        scores.append(score)

        history.write('%s %s %s %s\n' % (cwnd, tput, perc_delay, score))

        shutil.rmtree(data_dir)

        if stop_condition(scores):
            break

        cwnd += 10

    history.close()


if __name__ == '__main__':
    main()
