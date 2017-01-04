#!/usr/bin/env python

import argparse
import subprocess
import os
import numpy as np
import pantheon_helpers
from tabulate import tabulate
import plot_summary
from helpers.pantheon_help import check_call


def get_difference(metric_1, metric_2):
    return '{:+.2%}'.format((metric_2 - metric_1) / metric_1)


parser = argparse.ArgumentParser()

parser.add_argument('experiment_1', help='Logs folder, xz archive, '
                    'or archive url from a pantheon run')
parser.add_argument('experiment_2', help='Logs folder, xz archive, '
                    'or archive url from a pantheon run')

args = parser.parse_args()

experiments = [args.experiment_1, args.experiment_2]
exp_dirs = []
for experiment in experiments:
    if experiment.endswith('.tar.xz'):
        if experiment.startswith('https://'):
            check_call(['wget', '-c', experiment])
            experiment = experiment[8:]  # strip https://
            experiment = experiment.split('/')[-1]  # strip url path
        check_call(['tar', 'xJf', experiment])
        experiment = experiment[:-7]  # strip .tar.xz
    exp_dirs.append(experiment)


exp1_data = plot_summary.PlotSummary(True, False, exp_dirs[0]).plot_summary()
exp2_data = plot_summary.PlotSummary(True, False, exp_dirs[1]).plot_summary()

'''
print(exp1_data)
print('\n')
print(exp2_data)
print('\n')
'''

exp_1_schemes = set(exp1_data.keys())
exp_2_schemes = set(exp2_data.keys())
common_schemes = exp_1_schemes & exp_2_schemes

throughput_lines = []
delay_lines = []
loss_lines = []

for scheme in common_schemes:
    exp1_tputs = [x[0] for x in exp1_data[scheme]]
    exp1_delays = [x[1] for x in exp1_data[scheme]]
    exp1_loss = [100. * x[2] for x in exp1_data[scheme]]

    exp2_tputs = [x[0] for x in exp2_data[scheme]]
    exp2_delays = [x[1] for x in exp2_data[scheme]]
    exp2_loss = [100. * x[2] for x in exp2_data[scheme]]

    exp1_runs = len(exp1_tputs)
    exp2_runs = len(exp2_tputs)

    exp1_throughput_mean = np.mean(exp1_tputs)
    exp2_throughput_mean = np.mean(exp2_tputs)

    exp1_throughput_std = np.std(exp1_tputs)
    exp2_throughput_std = np.std(exp2_tputs)

    throughput_lines.append([
        scheme, exp1_runs, exp2_runs, 'throughput (Mbit/s)',
        exp1_throughput_mean, exp2_throughput_mean,
        get_difference(exp1_throughput_mean, exp2_throughput_mean),
        exp1_throughput_std, exp2_throughput_std,
        get_difference(exp1_throughput_std, exp2_throughput_std)])

    exp1_delay_mean = np.mean(exp1_delays)
    exp2_delay_mean = np.mean(exp2_delays)
    exp1_delay_std = np.std(exp1_delays)
    exp2_delay_std = np.std(exp2_delays)

    delay_lines.append([
        scheme, exp1_runs, exp2_runs, '95th percentile delay (ms)',
        exp1_delay_mean, exp2_delay_mean,
        get_difference(exp1_delay_mean, exp2_delay_mean),
        exp1_delay_std, exp2_delay_std,
        get_difference(exp1_delay_std, exp2_delay_std)])

    exp1_loss_mean = np.mean(exp1_loss)
    exp2_loss_mean = np.mean(exp2_loss)
    exp1_loss_std = np.std(exp1_loss)
    exp2_loss_std = np.std(exp2_loss)

    loss_lines.append([
        scheme, exp1_runs, exp2_runs, '% loss rate',
        exp1_loss_mean, exp2_loss_mean,
        get_difference(exp1_loss_mean, exp2_loss_mean),
        exp1_loss_std, exp2_loss_std,
        get_difference(exp1_loss_std, exp2_loss_std)])

output_headers = [
    'scheme', 'exp 1 runs', 'exp 2 runs', 'aggregate metric', 'mean 1',
    'mean 2', '% difference', 'std dev 1', 'std dev 2', '% difference']

print('Comparison of: %s and %s' % (exp_dirs[0], exp_dirs[1]))
print tabulate(throughput_lines + delay_lines + loss_lines,
               headers=output_headers, floatfmt=".2f", stralign="right")
