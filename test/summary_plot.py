#!/usr/bin/env python

import os
import sys
import re
from os import path
from parse_arguments import parse_arguments
from subprocess import check_output

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.markers as markers


def get_delay_throughput(log_name):
    stats_log = open(log_name)
    throughput = None
    delay = None

    for line in stats_log:
        result = re.match(r'Average throughput: (.*?) Mbit/s', line)
        if result:
            throughput = result.group(1)

        result = re.match(r'95th percentile per-packet one-way delay: '
                          '(.*?) ms', line)
        if result:
            delay = result.group(1)

        if throughput and delay:
            break

    stats_log.close()
    return (delay, throughput)


def plot_summary(data, pretty_names, pantheon_summary_png):
    min_delay = None
    color_i = 0
    marker_i = 0
    color_names = colors.cnames.keys()
    marker_names = markers.MarkerStyle.filled_markers

    for cc, value in data.items():
        cc_name = pretty_names[cc]
        color = color_names[color_i]
        marker = marker_names[marker_i]
        x_data, y_data = zip(*value)
        plt.scatter(x_data, y_data, color=color, marker=marker, label=cc_name)
        color_i = color_i + 1 if color_i < len(color_names) - 1 else 0
        marker_i = marker_i + 1 if marker_i < len(marker_names) - 1 else 0

        cc_min_delay = min(x_data)
        if not min_delay or cc_min_delay < min_delay:
            min_delay = cc_min_delay

    axes = plt.gca()

    xticks = axes.get_xticks()
    if min_delay >= 0 and xticks[0] <= 0:
        x_interval = xticks[1] - xticks[0]
        xmin = -x_interval / 5
        axes.set_xlim(left=xmin)

    plt.legend(scatterpoints=1, bbox_to_anchor=(1, 0.5), loc='center left')
    plt.xlabel('95th percentile of per-packet one-way delay (ms)')
    plt.ylabel('Average throughput (Mbit/s)')
    plt.title('Summary of results')
    plt.grid()
    plt.savefig(pantheon_summary_png, dpi=300,
                bbox_inches='tight', pad_inches=0.2)


def main():
    args = parse_arguments(path.basename(__file__))

    test_dir = path.abspath(path.dirname(__file__))
    src_dir = path.abspath(path.join(test_dir, '../src'))
    pantheon_summary_png = path.join(test_dir, 'pantheon_summary.png')

    pretty_names = {}
    data = {}
    for cc in args.cc_schemes:
        if cc not in pretty_names:
            cc_name = check_output(
                ['python', path.join(src_dir, cc + '.py'), 'friendly_name'])
            pretty_names[cc] = cc_name if cc_name else cc
            pretty_names[cc] = pretty_names[cc].strip().replace('_', '\\_')
            data[cc] = []

        for run_id in xrange(1, 1 + args.run_times):
            log_name = path.join(test_dir, '%s_stats_run%s.log' % (cc, run_id))
            data[cc].append(get_delay_throughput(log_name))

    plot_summary(data, pretty_names, pantheon_summary_png)


if __name__ == '__main__':
    main()
