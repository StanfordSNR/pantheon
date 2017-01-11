#!/usr/bin/env python

import argparse
import subprocess
import os
import numpy as np
import pantheon_helpers
from tabulate import tabulate
import plot_summary
from helpers.pantheon_help import check_call
import get_experiment_stats


def get_diff(metric_1, metric_2):
    return (metric_2 - metric_1) / metric_1


def difference_str(metric_1, metric_2):
    return '{:+.2%}'.format(get_diff(metric_1, metric_2))


parser = argparse.ArgumentParser()

parser.add_argument('experiment_1', help='Logs folder, xz archive, '
                    'or archive url from a pantheon run')
parser.add_argument('experiment_2', help='Logs folder, xz archive, '
                    'or archive url from a pantheon run')
parser.add_argument('--analyze-schemes', metavar='\"SCHEME_1 SCHEME_2..\"',
                    help='what congestion control schemes to analyze '
                    '(default: is contents of pantheon_metadata.json')
parser.add_argument('--no-pickle', action='store_true', dest='no_pickle',
                    help='don\'t try to load stats from pickle file (only '
                    'tries when using --analyze schemes')

args = parser.parse_args()
exp1_stats = get_experiment_stats.get_experiment_stats(args.experiment_1,
                                                       args.analyze_schemes,
                                                       args.no_pickle)
exp2_stats = get_experiment_stats.get_experiment_stats(args.experiment_2,
                                                       args.analyze_schemes,
                                                       args.no_pickle)


exp_1_schemes = set(exp1_stats.keys())
exp_2_schemes = set(exp2_stats.keys())
common_schemes = exp_1_schemes & exp_2_schemes

throughput_lines = []
delay_lines = []
loss_lines = []

tput_median_score = 0.0
delay_median_score = 0.0
tput_std_score = 0.0
delay_std_score = 0.0

score_candidate_schemes = ['default_tcp', 'vegas', 'ledbat', 'pcc', 'verus',
                           'scream', 'sprout', 'webrtc', 'quic']
score_schemes = []

for scheme in sorted(common_schemes):
    exp1 = exp1_stats[scheme]
    exp2 = exp2_stats[scheme]
    if scheme in score_candidate_schemes:
        tput_median_score += abs(get_diff(exp1.throughput_median,
                                          exp2.throughput_median))
        delay_median_score += abs(get_diff(exp1.delay_median,
                                           exp2.delay_median))

        tput_std_score += abs(get_diff(exp1.throughput_std,
                                       exp2.throughput_std))
        delay_std_score += abs(get_diff(exp1.delay_std,
                                        exp2.delay_std))

        score_schemes.append(scheme)
        scheme = '*' + scheme

    throughput_lines.append([
        scheme, exp1.runs, exp2.runs, 'throughput (Mbit/s)',
        exp1.throughput_median, exp2.throughput_median,
        difference_str(exp1.throughput_median, exp2.throughput_median),
        exp1.throughput_std, exp2.throughput_std,
        difference_str(exp1.throughput_std, exp2.throughput_std)])

    delay_lines.append([
        scheme, exp1.runs, exp2.runs, '95th percentile delay (ms)',
        exp1.delay_median, exp2.delay_median,
        difference_str(exp1.delay_median, exp2.delay_median),
        exp1.delay_std, exp2.delay_std,
        difference_str(exp1.delay_std, exp2.delay_std)])

    loss_lines.append([
        scheme, exp1.runs, exp2.runs, '% loss rate',
        exp1.loss_median, exp2.loss_median,
        difference_str(exp1.loss_median, exp2.loss_median),
        exp1.loss_std, exp2.loss_std,
        difference_str(exp1.loss_std, exp2.loss_std)])

output_headers = [
    'scheme', 'exp 1 runs', 'exp 2 runs', 'aggregate metric', 'median 1',
    'median 2', '% difference', 'std dev 1', 'std dev 2', '% difference']

print('Comparison of: %s and %s' % (args.experiment_1, args.experiment_2))
print tabulate(throughput_lines + delay_lines + loss_lines,
               headers=output_headers, floatfmt=".2f", stralign="right")

print('*Average median throughput difference for %s is:' %
      ', '.join(sorted(score_schemes)))
print('{:.2%}'.format(tput_median_score / len(score_schemes)))

print('*Average median delay difference for delay for %s is:' %
      ', '.join(sorted(score_schemes)))
print('{:.2%}'.format(delay_median_score / len(score_schemes)))

print('*Average stddev throughput difference for %s is:' %
      ', '.join(sorted(score_schemes)))
print('{:.2%}'.format(tput_std_score / len(score_schemes)))

print('*Average stddev delay difference for %s is:' %
      ', '.join(sorted(score_schemes)))
print('{:.2%}'.format(delay_std_score / len(score_schemes)))
