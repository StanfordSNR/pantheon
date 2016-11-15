#!/usr/bin/env python

import re
import sys
import math
from os import path
from time import strftime
from datetime import datetime
from pantheon_help import check_output, get_friendly_names
from parse_arguments import parse_arguments

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.markers as markers
import matplotlib.ticker as ticker


class PlotSummary:
    def __init__(self, args):
        self.test_dir = path.abspath(path.dirname(__file__))
        self.src_dir = path.abspath(path.join(self.test_dir, '../src'))
        self.run_times = args.run_times
        self.cc_schemes = args.cc_schemes
        self.timezone = None

    def parse_stats_log(self, log_name):
        stats_log = open(log_name)

        start_time = None
        end_time = None
        throughput = None
        delay = None
        worst_abs_ofst = None

        for line in stats_log:
            ret = re.match(r'Start at: (.*)', line)
            if ret:
                start_time = ret.group(1).rsplit(' ', 1)
                if not self.timezone:
                    self.timezone = start_time[1]
                start_time = start_time[0]
                continue

            ret = re.match(r'End at: (.*)', line)
            if ret:
                end_time = ret.group(1).rsplit(' ', 1)[0]
                continue

            ret = re.match(r'Average throughput: (.*?) Mbit/s', line)
            if ret:
                if not throughput:
                    throughput = float(ret.group(1))
                continue

            ret = re.match(r'95th percentile per-packet one-way delay: '
                           '(.*?) ms', line)
            if ret:
                if not delay:
                    delay = float(ret.group(1))
                continue

            ret = re.match(r'\* Worst absolute clock offset: (.*?) ms', line)
            if ret:
                worst_abs_ofst = float(ret.group(1))
                continue

        stats_log.close()
        return (start_time, end_time, throughput, delay, worst_abs_ofst)

    def process_stats_logs(self):
        self.data = {}
        self.time_series_data = []
        self.worst_abs_ofst = None
        time_format = '%a, %d %b %Y %H:%M:%S'

        for cc in self.cc_schemes:
            self.data[cc] = []
            cc_name = self.friendly_names[cc]

            for run_id in xrange(1, 1 + self.run_times):
                log = path.join(
                    self.test_dir, '%s_stats_run%s.log' % (cc, run_id))
                (start_t, end_t, tput, delay, ofst) = self.parse_stats_log(log)

                self.data[cc].append((tput, delay))
                if ofst:
                    if not self.worst_abs_ofst or ofst > self.worst_abs_ofst:
                        self.worst_abs_ofst = ofst

                start_datetime = datetime.strptime(start_t, time_format)
                end_datetime = datetime.strptime(end_t, time_format)
                self.time_series_data.append(
                    (start_datetime, end_datetime, tput, delay, cc_name))

    def plot_throughput_delay(self):
        min_delay = None
        max_delay = None
        color_i = 0
        marker_i = 0
        color_names = ['r', 'y', 'b', 'g', 'c', 'm', 'brown', 'orange', 'gray',
                       'gold', 'skyblue', 'olive', 'lime', 'violet', 'purple']
        marker_names = markers.MarkerStyle.filled_markers

        fig_raw, ax_raw = plt.subplots()
        fig_mean, ax_mean = plt.subplots()

        for cc, value in self.data.items():
            cc_name = self.friendly_names[cc]
            color = color_names[color_i]
            marker = marker_names[marker_i]
            y_data, x_data = zip(*value)

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
            if self.worst_abs_ofst:
                xlabel += ('\n(worst absolute clock offset: %s ms)' %
                           self.worst_abs_ofst)
            ax.set_xlabel(xlabel)
            ax.set_ylabel('Average throughput (Mbit/s)')
            ax.grid()

        # save pantheon_summary.png
        ax_raw.set_title('Summary of results')
        lgd = ax_raw.legend(scatterpoints=1, bbox_to_anchor=(1, 0.5),
                            loc='center left', fontsize=12)
        raw_summary = path.join(self.test_dir, 'pantheon_summary.png')
        fig_raw.savefig(raw_summary, dpi=300, bbox_extra_artists=(lgd,),
                        bbox_inches='tight', pad_inches=0.2)

        # save pantheon_summary_mean.png
        ax_mean.set_title('Summary of results (average of all runs)')
        mean_summary = path.join(
            self.test_dir, 'pantheon_summary_mean.png')
        fig_mean.savefig(mean_summary, dpi=300,
                         bbox_inches='tight', pad_inches=0.2)

    def autolabel(self, rects, ax, friendly_names):
        i = 0
        for rect in rects:
            ax.text(rect.get_x() + rect.get_width() / 2.0,
                    rect.get_height() + 0.2,
                    friendly_names[i], ha='center', va='bottom')
            i += 1

    def plot_throughput_time(self):
        # prepare data for x and y axes to plot
        self.time_series_data.sort()
        init_datetime = self.time_series_data[0][0]
        init_time_readable = init_datetime.strftime('%a, %d %b %Y %H:%M:%S')
        init_time_readable += ' ' + self.timezone

        x_start_time = []
        x_end_time = []
        y_throughput = []
        label_friendly_names = []
        for item in self.time_series_data:
            x_start_time.append((item[0] - init_datetime).total_seconds())
            x_end_time.append((item[1] - init_datetime).total_seconds())
            y_throughput.append(item[2])
            label_friendly_names.append(item[-1])

        # ticks and labels
        x_range = range(len(self.time_series_data))
        x_ticks = []
        x_tick_labels = []

        for i in x_range:
            x_ticks += [i, i + 0.5]

        for pair in zip(x_start_time, x_end_time):
            x_tick_labels += [pair[0], pair[1]]

        # plot throughput against time
        fig, ax_tput = plt.subplots()

        rects = ax_tput.bar(x_range, y_throughput, width=0.5, color='grey')
        ax_tput.set_xlabel('Time (s) since ' + init_time_readable)
        ax_tput.set_xticks(x_ticks)
        ax_tput.set_xticklabels(x_tick_labels, rotation=45)
        ax_tput.set_xlim(left=-0.5)
        ax_tput.set_ylabel('Average throughput (Mbit/s)')
        ax_tput.grid()
        self.autolabel(rects, ax_tput, label_friendly_names)

        (fig_w, fig_h) = fig.get_size_inches()
        fig.set_size_inches(1.5 * len(x_range), fig_h)

        time_series = path.join(self.test_dir, 'pantheon_time_series.png')
        fig.savefig(time_series, dpi=300, bbox_inches='tight', pad_inches=0.2)

    def plot_summary(self):
        self.friendly_names = get_friendly_names(self.cc_schemes)
        self.process_stats_logs()
        self.plot_throughput_delay()
        self.plot_throughput_time()


def main():
    args = parse_arguments(path.basename(__file__))

    plot_summary = PlotSummary(args)
    plot_summary.plot_summary()


if __name__ == '__main__':
    main()
