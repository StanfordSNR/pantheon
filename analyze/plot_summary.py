#!/usr/bin/env python

import os
import re
import sys
import math
import json
import numpy
import pantheon_helpers
import matplotlib_agg
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import multiprocessing
import tunnel_graph
from os import path
from time import strftime
from datetime import datetime
from multiprocessing.pool import ThreadPool
from helpers.pantheon_help import (check_output, get_friendly_names, Popen,
                                   PIPE, get_color_names, get_marker_names)
from helpers.parse_arguments import parse_arguments


class PlotSummary:
    def __init__(self, no_plots, include_acklink, data_dir, schemes):
        self.data_dir = path.abspath(data_dir)
        analyze_dir = path.dirname(__file__)
        self.tunnel_graph = path.join(analyze_dir, 'tunnel_graph.py')
        self.src_dir = path.abspath(path.join(analyze_dir, '../src'))

        # load pantheon_metadata.json as a dictionary
        metadata_fname = path.join(self.data_dir, 'pantheon_metadata.json')
        with open(metadata_fname) as metadata_file:
            metadata_dict = json.load(metadata_file)

        self.run_times = metadata_dict['run_times']
        self.flows = int(metadata_dict['flows'])
        self.timezone = None
        self.runtime = int(metadata_dict['runtime'])

        self.include_acklink = include_acklink
        self.no_plots = no_plots

        if schemes:
            self.cc_schemes = schemes.split()
            assert set(self.cc_schemes).issubset(
                    set(metadata_dict['cc_schemes'].split())), (
                    '--analyze-schemes %s has schemes not in experiment '
                    '(%s)' % (self.cc_schemes,
                              metadata_dict['cc_schemes'].split()))
        else:
            self.cc_schemes = metadata_dict['cc_schemes'].split()

        self.experiment_title = ''
        if ('remote_information' in metadata_dict and
                'local_information' in metadata_dict):

            remote_txt = metadata_dict['remote_information']
            if 'remote_interface' in metadata_dict:
                remote_txt += ' ' + metadata_dict['remote_interface']
            else:
                remote_txt += ' Ethernet'

            local_txt = metadata_dict['local_information'] + ' Ethernet'
            if metadata_dict['sender_side'] == 'remote':
                uploader = remote_txt
                downloader = local_txt
            else:
                uploader = local_txt
                downloader = remote_txt

            self.experiment_title += '%s to %s ' % (uploader, downloader)

        self.experiment_title += ('%s runs of %ss each per scheme'
                                  % (metadata_dict['run_times'],
                                     metadata_dict['runtime']))

    def parse_tunnel_log(self, cc, run_id):
        log_prefix = cc
        if self.flows == 0:
            log_prefix += '_mm'

        tput = None
        delay = None
        loss = None
        for_stats = None

        procs = []
        error = False

        link_directions = ['datalink']
        if self.include_acklink:
            link_directions.append('acklink')

        for link_t in link_directions:
            log_name = log_prefix + '_%s_run%s.log' % (link_t, run_id)
            log_path = path.join(self.data_dir, log_name)

            if not path.isfile(log_path):
                sys.stderr.write('Warning: %s does not exist\n' % log_path)
                error = True
                continue

            if self.no_plots:
                tput_graph_path = None
                delay_graph_path = None
            else:
                tput_graph = cc + '_%s_throughput_run%s.png' % (link_t, run_id)
                tput_graph_path = path.join(self.data_dir, tput_graph)

                delay_graph = cc + '_%s_delay_run%s.png' % (link_t, run_id)
                delay_graph_path = path.join(self.data_dir, delay_graph)

            try:
                sys.stderr.write("tunnel_graph %s\n" % log_path)
                run_analysis = tunnel_graph.TunnelGraph(500, log_path,
                                                        tput_graph_path,
                                                        delay_graph_path
                                                        ).tunnel_graph()
            except:
                sys.stderr.write('Warning: "tunnel_graph %s" failed with an '
                                 'exception.\n' % log_path)
                error = True

            if error:
                continue

            if link_t == 'datalink':
                (tput, delay, loss, test_runtime, for_stats, max_prop_delay, min_prop_delay, max_total_throughput_in_a_bin) = run_analysis

                max_outstanding_packets = int(check_output(['python', 'max_outstanding_packets.py', log_path]))
                print(max_outstanding_packets)
                if test_runtime < (750 * self.runtime):  # .75 * 1000 ms/s
                    sys.stderr.write('Warning: "tunnel_graph %s" had duration '
                                     '%.2f seconds but should have been around'
                                     ' %d seconds. Ignoring this run.\n' %
                                     (log_path, (test_runtime / 1000.),
                                      self.runtime))
                    error = True

        if error:
            return (None, None, None, None, None, None, None, None)
        else:
            return (tput, delay, loss, for_stats, max_prop_delay, min_prop_delay, max_total_throughput_in_a_bin, max_outstanding_packets)

    def parse_stats_log(self, cc, run_id, for_stats):
        stats_log_path = path.join(
            self.data_dir, '%s_stats_run%s.log' % (cc, run_id))
        if not path.isfile(stats_log_path):
            sys.stderr.write('Warning: %s does not exist\n' % stats_log_path)
            return None

        ofst = None
        stats_log = open(stats_log_path, 'r+')

        for_stats_exists = False
        for line in stats_log:
            ret = re.match(r'Worst absolute clock offset: (.*?) ms', line)
            if ret and not ofst:
                ofst = float(ret.group(1))
                continue

            ret = re.match(r'# Datalink statistics', line)
            if ret:
                for_stats_exists = True
                break

        if not for_stats_exists and for_stats:
            stats_log.seek(0, os.SEEK_END)
            stats_log.write('\n# Datalink statistics (generated by %s)\n'
                            % path.basename(__file__))
            stats_log.write('%s' % for_stats)

        stats_log.close()
        return ofst

    def generate_data(self):
        self.data = {}
        self.worst_abs_ofst = None
        time_format = '%a, %d %b %Y %H:%M:%S'

        for cc in self.cc_schemes:
            self.data[cc] = []
            cc_name = self.friendly_names[cc]

            pool = ThreadPool(processes=min(multiprocessing.cpu_count(),
                                            self.run_times))
            results = dict()
            for run_id in xrange(1, 1 + self.run_times):
                results[run_id] = pool.apply_async(self.parse_tunnel_log,
                                                   args=(cc, run_id))

            for run_id in xrange(1, 1 + self.run_times):
                (tput, delay, loss_rate, for_stats, max_prop_delays, min_prop_delays, max_total_throughput_in_a_bins, max_outstanding_packets) = results[run_id].get()
                ofst = self.parse_stats_log(cc, run_id, for_stats)

                if not tput or not delay:
                    continue

                self.data[cc].append((tput, delay, loss_rate, max_prop_delays, min_prop_delays, max_total_throughput_in_a_bins, max_outstanding_packets))
                if ofst:
                    if not self.worst_abs_ofst or ofst > self.worst_abs_ofst:
                        self.worst_abs_ofst = ofst

        return self.data

    def plot_throughput_delay(self):
        min_delay = None
        color_names = get_color_names(self.cc_schemes)
        marker_names = get_marker_names(self.cc_schemes)

        fig_raw, ax_raw = plt.subplots()
        fig_mean, ax_mean = plt.subplots()

        for cc in self.data:
            if not self.data[cc]:
                continue

            value = self.data[cc]
            cc_name = self.friendly_names[cc]
            color = color_names[cc]
            marker = marker_names[cc]
            y_data, x_data, _, _, _, _, _ = zip(*value)

            # find min and max delay
            cc_min_delay = min(x_data)
            if not min_delay or cc_min_delay < min_delay:
                min_delay = cc_min_delay

            # plot raw values
            ax_raw.scatter(x_data, y_data, color=color, marker=marker,
                           label=cc_name, clip_on=False)

            # plot the average of raw values
            x_mean = sum(x_data) / len(x_data)
            y_mean = sum(y_data) / len(y_data)
            ax_mean.scatter(x_mean, y_mean, color=color, marker=marker,
                            clip_on=False)
            ax_mean.annotate(cc_name, (x_mean, y_mean))

        for fig, ax in [(fig_raw, ax_raw), (fig_mean, ax_mean)]:
            if min_delay > 0:
                ax.set_xscale('log', basex=2)
                ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
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
        ax_raw.set_title(self.experiment_title, y=1.02, fontsize=12)
        lgd = ax_raw.legend(scatterpoints=1, bbox_to_anchor=(1, 0.5),
                            loc='center left', fontsize=12)
        raw_summary = path.join(self.data_dir, 'pantheon_summary.png')
        fig_raw.savefig(raw_summary, dpi=300, bbox_extra_artists=(lgd,),
                        bbox_inches='tight', pad_inches=0.2)

        # save pantheon_summary_mean.png
        ax_mean.set_title(self.experiment_title +
                          '\nmean of all runs by scheme', fontsize=12)
        mean_summary = path.join(
            self.data_dir, 'pantheon_summary_mean.png')
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

        numpy.median([1, 2]) # break early if no numpy
        self.friendly_names = get_friendly_names(self.cc_schemes)
        data = self.generate_data()
        if not self.no_plots:
            self.plot_throughput_delay()

        all_max_delays = []
        all_min_delays = []
        all_max_throughputs = []
        all_tputs = []
        all_max_outstanding_packets = []
        all_loss_rates = []
        for cc in self.cc_schemes:
            tputs, _, losses, max_delays, min_delays, max_throughputs, max_outstanding_packets = zip(*self.data[cc])
            all_max_delays += max_delays
            all_min_delays += min_delays
            all_max_throughputs += max_throughputs
            all_tputs += tputs
            all_max_outstanding_packets += max_outstanding_packets
            all_loss_rates += losses

        median_delay =  numpy.median(all_min_delays)
        max_delay_bound = median_delay

        min_delay = min(all_min_delays)
        min_delay_bound = round(float(min_delay)*.7)

        max_throughput = max(all_max_throughputs)
        max_throughput_bound = float(max_throughput)*1.2

        min_throughput = numpy.median(all_max_throughputs)
        min_throughput_bound = min_throughput

        max_outstanding_packets = max(all_max_outstanding_packets)

        median_loss_rate = numpy.median(all_loss_rates)
        max_loss_bound = median_loss_rate

        print("real limits: median prop delay %d, min prop delay %d, max throughput in a bin %.2f, min average throughput %.2f, outstanding packets %d, median loss rate %.4f" % (median_delay, min_delay, max_throughput, min_throughput, max_outstanding_packets, median_loss_rate))
        print("bounds: max_delay_bound %d, min_delay_bound %d, max_throughput_bound %.2f, min_throughput_bound %.2f,  min_loss_bound 0, max_loss_bound %.4f" % (max_delay_bound, min_delay_bound, max_throughput_bound, min_throughput_bound, max_loss_bound))
        return data


def main():
    args = parse_arguments(path.basename(__file__))

    plot_summary = PlotSummary(args.no_plots, args.include_acklink,
                               args.data_dir, args.analyze_schemes)
    plot_summary.plot_summary()


if __name__ == '__main__':
    DEVNULL = open(os.devnull, 'w')
    main()
    DEVNULL.close()
