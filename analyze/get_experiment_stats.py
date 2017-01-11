#!/usr/bin/env python

import argparse
import subprocess
import os
import numpy as np
import pantheon_helpers
from tabulate import tabulate
import plot_summary
from helpers.pantheon_help import check_call
from collections import namedtuple

SchemeStats = namedtuple('SchemeStats', 'runs, throughput_median, '
                         'throughput_std, delay_median, delay_std, '
                         'loss_median, loss_std')


def get_experiment_stats(experiment_folder, only_schemes):
    exp_data = plot_summary.PlotSummary(True, False, experiment_folder,
                                        only_schemes).plot_summary()

    stats = dict()
    for scheme in exp_data.keys():
        tputs = [x[0] for x in exp_data[scheme]]
        delays = [x[1] for x in exp_data[scheme]]
        loss = [100. * x[2] for x in exp_data[scheme]]

        runs = len(tputs)

        throughput_median = np.median(tputs)
        throughput_std = np.std(tputs)

        delay_median = np.median(delays)
        delay_std = np.std(delays)

        loss_median = np.median(loss)
        loss_std = np.std(loss)

        stats[scheme] = SchemeStats(runs, throughput_median, throughput_std,
                                    delay_median, delay_std, loss_median,
                                    loss_std)
    return stats


def print_stats(stats_dict):
    for (scheme, (runs, throughput_median, throughput_std, delay_median,
         delay_std, loss_median, loss_std)) in stats.iteritems():
        print('scheme=%s, runs=%d, throughput_median=%f, throughput_std=%f,'
              'delay_median=%f, delay_std=%f, loss_median=%f, '
              'loss_std=%f' % (scheme, runs, throughput_median, throughput_std,
                               delay_median, delay_std, loss_median, loss_std))


def get_experiment_folder(experiment_arg):
    experiment = experiment_arg
    if experiment.endswith('.tar.xz'):
        if experiment.startswith('https://'):
            check_call(['wget', '-c', experiment])
            experiment = experiment[8:]  # strip https://
            experiment = experiment.split('/')[-1]  # strip url path
        check_call(['tar', 'xJf', experiment])
        experiment = experiment[:-7]  # strip .tar.xz
    return experiment

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('experiment', help='Logs folder, xz archive, '
                        'or archive url from a pantheon run')
    parser.add_argument('--analyze-schemes', metavar='\"SCHEME_1 SCHEME_2..\"',
                        help='what congestion control schemes to analyze '
                        '(default: is contents of pantheon_metadata.json')

    args = parser.parse_args()
    experiment_folder = get_experiment_folder(args.experiment)
    stats = get_experiment_stats(experiment_folder, args.analyze_schemes)
    print_stats(stats)
