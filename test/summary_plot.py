#!/usr/bin/env python

import os
import sys
import re
import math
from os import path
from parse_arguments import parse_arguments
from subprocess import check_output

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.markers as markers
import matplotlib.ticker as ticker


def parse_stats(log_name):
    stats_log = open(log_name)
    throughput = None
    delay = None
    worst_local_offset = None
    worst_remote_offset = None

    for line in stats_log:
        result = re.match(r'Average throughput: (.*?) Mbit/s', line)
        if result and not throughput:
            throughput = float(result.group(1))

        result = re.match(r'95th percentile per-packet one-way delay: '
                          '(.*?) ms', line)
        if result and not delay:
            delay = float(result.group(1))

        result = re.match(r'Local clock offset: (.*?) ms', line)
        if result:
            ofst = float(result.group(1))
            if not worst_local_offset or abs(ofst) > worst_local_offset:
                worst_local_offset = ofst

        result = re.match(r'Remote clock offset: (.*?) ms', line)
        if result:
            ofst = float(result.group(1))
            if not worst_remote_offset or abs(ofst) > worst_remote_offset:
                worst_remote_offset = ofst

    stats_log.close()
    return (delay, throughput, worst_local_offset, worst_remote_offset)


def plot_summary(data, worst_offsets, pretty_names,
                 raw_summary_png, mean_summary_png):
    min_delay = None
    max_delay = None
    color_i = 0
    marker_i = 0
    color_names = ['r', 'y', 'b', 'g', 'c', 'm', 'brown', 'orange', 'gray',
                   'gold', 'skyblue', 'olive', 'lime', 'violet', 'purple']
    marker_names = markers.MarkerStyle.filled_markers

    fig_raw, ax_raw = plt.subplots()
    fig_mean, ax_mean = plt.subplots()

    for cc, value in data.items():
        cc_name = pretty_names[cc]
        color = color_names[color_i]
        marker = marker_names[marker_i]
        x_data, y_data = zip(*value)

        # find min and max delay
        cc_min_delay = min(x_data)
        if not min_delay or cc_min_delay < min_delay:
            min_delay = cc_min_delay

        cc_max_delay = max(x_data)
        if not max_delay or cc_max_delay > max_delay:
            max_delay = cc_max_delay

        # plot raw values
        ax_raw.scatter(x_data, y_data, color=color, marker=marker,
                       label=cc_name, clip_on=False)

        # plot the average of raw values
        x_mean = sum(x_data) / len(x_data)
        y_mean = sum(y_data) / len(y_data)
        ax_mean.scatter(x_mean, y_mean, color=color, marker=marker,
                        clip_on=False)
        ax_mean.annotate(cc_name, (x_mean, y_mean))

        color_i = color_i + 1 if color_i < len(color_names) - 1 else 0
        marker_i = marker_i + 1 if marker_i < len(marker_names) - 1 else 0

    # find min and max of x ticks
    if min_delay > 0:
        log_min_delay = math.log(float(min_delay), 2)
        log_max_delay = math.log(float(max_delay), 2)
        xmin = pow(2, math.floor(log_min_delay))
        xmax = pow(2, math.ceil(log_max_delay))
        xmin /= math.sqrt(2)
        xmax *= math.sqrt(2)

    for fig, ax in [(fig_raw, ax_raw), (fig_mean, ax_mean)]:
        if min_delay > 0 and xmax > 4 * xmin:
            ax.set_xscale('log', basex=2)
            ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
            ax.set_xlim(left=xmin, right=xmax)
        ax.invert_xaxis()

        yticks = ax.get_yticks()
        if yticks[0] < 0:
            ax.set_ylim(bottom=0)

        xlabel = '95th percentile of per-packet one-way delay (ms)'
        if worst_offsets[0] and worst_offsets[1]:
            xlabel += ('\n(worst clock offset: local %s ms, remote %s ms)' %
                       worst_offsets)
        ax.set_xlabel(xlabel)
        ax.set_ylabel('Average throughput (Mbit/s)')
        ax.grid()

    # save pantheon_summary.png
    ax_raw.set_title('Summary of results')
    lgd = ax_raw.legend(scatterpoints=1, bbox_to_anchor=(1, 0.5),
                        loc='center left', fontsize=12)
    fig_raw.savefig(raw_summary_png, dpi=300, bbox_extra_artists=(lgd,),
                    bbox_inches='tight', pad_inches=0.2)

    # save pantheon_summary_mean.png
    ax_mean.set_title('Summary of results (average of all runs)')
    fig_mean.savefig(mean_summary_png, dpi=300,
                     bbox_inches='tight', pad_inches=0.2)


def main():
    args = parse_arguments(path.basename(__file__))

    test_dir = path.abspath(path.dirname(__file__))
    src_dir = path.abspath(path.join(test_dir, '../src'))
    raw_summary_png = path.join(test_dir, 'pantheon_summary.png')
    mean_summary_png = path.join(test_dir, 'pantheon_summary_mean.png')

    pretty_names = {}
    data = {}
    worst_local_ofst = None
    worst_remote_ofst = None
    for cc in args.cc_schemes:
        if cc not in pretty_names:
            cc_name = check_output(
                ['python', path.join(src_dir, cc + '.py'), 'friendly_name'])
            pretty_names[cc] = cc_name if cc_name else cc
            pretty_names[cc] = pretty_names[cc].strip().replace('_', '\\_')
            data[cc] = []

        for run_id in xrange(1, 1 + args.run_times):
            log_name = path.join(test_dir, '%s_stats_run%s.log' % (cc, run_id))
            delay, throughput, local_ofst, remote_ofst = parse_stats(log_name)
            data[cc].append((delay, throughput))
            if local_ofst:
                if not worst_local_ofst or abs(local_ofst) > worst_local_ofst:
                    worst_local_ofst = local_ofst
            if remote_ofst:
                if (not worst_remote_ofst or
                        abs(remote_ofst) > worst_remote_ofst):
                    worst_remote_ofst = remote_ofst

    worst_offsets = (worst_local_ofst, worst_remote_ofst)
    plot_summary(data, worst_offsets, pretty_names,
                 raw_summary_png, mean_summary_png)


if __name__ == '__main__':
    main()
