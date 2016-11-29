#!/usr/bin/env python

import re
import sys
import math
import json
from os import path, devnull
from time import strftime
from datetime import datetime
import pantheon_helpers
from helpers.pantheon_help import check_output, get_friendly_names, Popen, PIPE
from helpers.parse_arguments import parse_arguments

import matplotlib_agg
import matplotlib.pyplot as plt
import matplotlib.markers as markers
import matplotlib.ticker as ticker


class PlotSummary:
    def __init__(self, analysis_dir, metadata_dict):
        self.analysis_dir = analysis_dir
        self.src_dir = path.abspath(path.join(self.analysis_dir, '../src'))
        self.run_times = metadata_dict['run_times']
        self.cc_schemes = metadata_dict['cc_schemes'].split()
        self.timezone = None

    def parse_stats_log(self, log_name, datalink_logname):
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

            ret = re.match(r'\* Worst absolute clock offset: (.*?) ms', line)
            if ret:
                worst_abs_ofst = float(ret.group(1))
                continue

        stats_log.close()

        cmd = ['mm-tunnel-throughput', '500', datalink_logname]
        proc = Popen(cmd, stdout=DEVNULL, stderr=PIPE)
        results = proc.communicate()[1]
        assert proc.returncode == 0

        ret = re.search(r'Average throughput: (.*?) Mbit/s', results)

        assert ret
        if not throughput:
            throughput = float(ret.group(1))

        cmd = ['mm-tunnel-delay', datalink_logname]
        proc = Popen(cmd, stdout=DEVNULL, stderr=PIPE)
        results = proc.communicate()[1]
        assert proc.returncode == 0

        ret = re.search(r'95th percentile per-packet one-way delay: '
                        '(.*?) ms', results)
        assert ret
        if not delay:
            delay = float(ret.group(1))

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
                    self.analysis_dir, '%s_stats_run%s.log' % (cc, run_id))
                datalink_log = path.join(
                    self.analysis_dir, '%s_datalink_run%s.log' % (cc, run_id))
                (start_t, end_t, tput, delay, ofst) = self.parse_stats_log(
                                                         log, datalink_log)

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
        raw_summary = path.join(self.analysis_dir, 'pantheon_summary.png')
        fig_raw.savefig(raw_summary, dpi=300, bbox_extra_artists=(lgd,),
                        bbox_inches='tight', pad_inches=0.2)

        # save pantheon_summary_mean.png
        ax_mean.set_title('Summary of results (average of all runs)')
        mean_summary = path.join(
            self.analysis_dir, 'pantheon_summary_mean.png')
        fig_mean.savefig(mean_summary, dpi=300,
                         bbox_inches='tight', pad_inches=0.2)

    def autolabel(self, rects, ax, friendly_names):
        i = 0
        for rect in rects:
            ax.text(rect.get_x() + rect.get_width() / 2.0,
                    rect.get_height() + 0.2,
                    friendly_names[i], ha='center', va='bottom')
            i += 1

    def plot_summary(self):
        self.friendly_names = get_friendly_names(self.cc_schemes)
        self.process_stats_logs()
        self.plot_throughput_delay()


def main():
    parse_arguments(path.basename(__file__))

    analysis_dir = path.abspath(path.dirname(__file__))
    # load pantheon_metadata.json as a dictionary
    metadata_fname = path.join(analysis_dir, 'pantheon_metadata.json')
    with open(metadata_fname) as metadata_file:
        metadata_dict = json.load(metadata_file)

    plot_summary = PlotSummary(analysis_dir, metadata_dict)
    plot_summary.plot_summary()


if __name__ == '__main__':
    DEVNULL = open(devnull, 'w')
    main()
    DEVNULL.close()
