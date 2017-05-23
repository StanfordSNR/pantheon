#!/usr/bin/env python

import os
from os import path
import re
import sys
import multiprocessing
from multiprocessing.pool import ThreadPool
import numpy as np
import matplotlib_agg
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import project_root
from parse_arguments import parse_arguments
from analyze_helpers import load_test_metadata, verify_schemes_with_meta
from helpers.helpers import parse_config, print_cmd
import tunnel_graph


class Plot(object):
    def __init__(self, data_dir=path.join(project_root.DIR, 'test'),
                 schemes=None, include_acklink=False, no_graphs=False):
        self.data_dir = path.abspath(data_dir)
        self.include_acklink = include_acklink
        self.no_graphs = no_graphs

        metadata_path = path.join(self.data_dir, 'pantheon_metadata.json')
        meta = load_test_metadata(metadata_path)
        self.cc_schemes = verify_schemes_with_meta(schemes, meta)

        self.run_times = meta['run_times']
        self.flows = meta['flows']
        self.runtime = meta['runtime']
        self.worst_clock_offset = None

        analyze_dir = path.join(project_root.DIR, 'analyze')
        self.tunnel_graph = path.join(analyze_dir, 'tunnel_graph.py')

        self.expt_title = self.generate_expt_title(meta)

    def generate_expt_title(self, meta):
        if meta['mode'] == 'local':
            expt_title = 'local test in mahimahi, '
        elif meta['mode'] == 'remote':
            txt = {}
            for side in ['local', 'remote']:
                txt[side] = [side]

                if '%s_desc' % side in meta:
                    txt[side].append(meta['%s_desc' % side])
                if '%s_if' % side in meta:
                    txt[side].append(meta['%s_if' % side])
                else:
                    txt[side].append('Ethernet')

                txt[side] = ' '.join(txt[side])

            if meta['sender_side'] == 'remote':
                sender = txt['remote']
                receiver = txt['local']
            else:
                receiver = txt['remote']
                sender = txt['local']

            expt_title = 'test from %s to %s, ' % (sender, receiver)

        expt_title += '%s runs of %ss each per scheme' % (
            meta['run_times'], meta['runtime'])

        return expt_title

    def parse_tunnel_log(self, cc, run_id):
        log_prefix = cc
        if self.flows == 0:
            log_prefix += '_mm'

        tput = None
        delay = None
        loss = None
        stats = None

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

            if self.no_graphs:
                tput_graph_path = None
                delay_graph_path = None
            else:
                tput_graph = cc + '_%s_throughput_run%s.png' % (link_t, run_id)
                tput_graph_path = path.join(self.data_dir, tput_graph)

                delay_graph = cc + '_%s_delay_run%s.png' % (link_t, run_id)
                delay_graph_path = path.join(self.data_dir, delay_graph)

            print_cmd('tunnel_graph %s\n' % log_path)
            try:
                tunnel_results = tunnel_graph.TunnelGraph(
                    tunnel_log=log_path,
                    throughput_graph=tput_graph_path,
                    delay_graph=delay_graph_path).run()
            except Exception as exception:
                sys.stderr.write('Error: %s\n' % exception)
                sys.stderr.write('Warning: "tunnel_graph %s" failed but '
                                 'continued to run.\n' % log_path)
                error = True

            if error:
                continue

            if link_t == 'datalink':
                tput = tunnel_results['throughput']
                delay = tunnel_results['delay']
                loss = tunnel_results['loss']
                duration = tunnel_results['duration'] / 1000.0
                stats = tunnel_results['stats']

                if (duration < 0.9 * self.runtime or
                        duration > 1.1 * self.runtime):
                    sys.stderr.write(
                        'Warning: "tunnel_graph %s" had duration %.2f seconds '
                        'but should have been around %d seconds. Ignoring this'
                        ' run.\n' % (log_path, duration, self.runtime))
                    error = True

        if error:
            return (None, None, None, None)
        else:
            return (tput, delay, loss, stats)

    def parse_stats_log(self, cc, run_id, stats):
        stats_log_path = path.join(
            self.data_dir, '%s_stats_run%s.log' % (cc, run_id))

        if not path.isfile(stats_log_path):
            sys.stderr.write('Warning: %s does not exist\n' % stats_log_path)
            return None

        offset = None
        stats_exists = False
        stats_log = open(stats_log_path, 'r+')

        for line in stats_log:
            ret = re.match(r'Worst absolute clock offset: (.*?) ms', line)
            if ret and offset is None:
                offset = float(ret.group(1))
                continue

            ret = re.match(r'# Datalink statistics', line)
            if ret:
                stats_exists = True
                break

        if not stats_exists and stats:
            stats_log.seek(0, os.SEEK_END)
            stats_log.write('\n# Datalink statistics (generated by %s)\n'
                            % path.basename(__file__))
            stats_log.write('%s' % stats)

        stats_log.close()
        return offset

    def eval_performance(self):
        self.data = {}

        results = {}
        for cc in self.cc_schemes:
            self.data[cc] = []
            results[cc] = {}

        cc_id = 0
        run_id = 1
        pool = ThreadPool(processes=multiprocessing.cpu_count())

        while cc_id < len(self.cc_schemes):
            cc = self.cc_schemes[cc_id]
            results[cc][run_id] = pool.apply_async(
                self.parse_tunnel_log, args=(cc, run_id))

            run_id += 1
            if run_id > self.run_times:
                run_id = 1
                cc_id += 1

        for cc in self.cc_schemes:
            for run_id in xrange(1, 1 + self.run_times):
                (tput, delay, loss, stats) = results[cc][run_id].get()
                offset = self.parse_stats_log(cc, run_id, stats)

                if tput is None or delay is None:
                    continue

                self.data[cc].append((tput, delay, loss))
                if offset:
                    if (self.worst_clock_offset is None or
                            offset > self.worst_clock_offset):
                        self.worst_clock_offset = offset

        return self.data

    def plot_throughput_delay(self):
        min_delay = None

        fig_raw, ax_raw = plt.subplots()
        fig_mean, ax_mean = plt.subplots()

        power_scores = []

        config = parse_config()
        for cc in self.data:
            if not self.data[cc]:
                continue

            value = self.data[cc]
            cc_name = config[cc]['friendly_name']
            color = config[cc]['color']
            marker = config[cc]['marker']
            y_data, x_data, _ = zip(*value)

            # find min and max delay
            cc_min_delay = min(x_data)
            if min_delay is None or cc_min_delay < min_delay:
                min_delay = cc_min_delay

            # plot raw values
            ax_raw.scatter(x_data, y_data, color=color, marker=marker,
                           label=cc_name, clip_on=False)

            # plot the average of raw values
            x_mean = sum(x_data) / len(x_data)
            y_mean = sum(y_data) / len(y_data)
            ax_mean.scatter(x_mean, y_mean, color=color, marker=marker,
                            clip_on=False)
            power_scores.append((float(y_mean) / float(x_mean), color))
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
            if self.worst_clock_offset is not None:
                xlabel += ('\n(worst absolute clock offset: %s ms)' %
                           self.worst_clock_offset)
            ax.set_xlabel(xlabel)
            ax.set_ylabel('Average throughput (Mbit/s)')
            ax.grid()

        # save pantheon_summary.png
        ax_raw.set_title(self.expt_title, y=1.02, fontsize=12)
        lgd = ax_raw.legend(scatterpoints=1, bbox_to_anchor=(1, 0.5),
                            loc='center left', fontsize=12)
        raw_summary = path.join(self.data_dir, 'pantheon_summary.png')
        fig_raw.savefig(raw_summary, dpi=300, bbox_extra_artists=(lgd,),
                        bbox_inches='tight', pad_inches=0.2)

        # save pantheon_summary_mean.png
        ax_mean.set_title(self.expt_title +
                          '\nmean of all runs by scheme', fontsize=12)
        mean_summary = path.join(
            self.data_dir, 'pantheon_summary_mean.png')
        fig_mean.savefig(mean_summary, dpi=300,
                         bbox_inches='tight', pad_inches=0.2)

        # make and save pantheon_summary_power.png
        x_max, x_min = ax_mean.get_xlim()
        y_min, y_max = ax_mean.get_ylim()
        power_score_lines = []

        ax_mean.set_autoscale_on(False)

        for power_score, color in power_scores:
            power_score_line = []

            for x in np.arange(x_min, x_max, (x_max - x_min) / 100.0):
                y = x * power_score
                if y <= y_max and y >= y_min:
                    power_score_line.append((x, y))
            for y in np.arange(y_min, y_max, (y_max - y_min) / 100.0):
                x = y / power_score
                if x <= x_max and x >= x_min:
                    power_score_line.append((x, y))

            power_score_line.sort()  # can have weird artifacts otherwise
            power_score_lines.append((power_score_line, color, power_score))

        for power_score_line, color, power_score in power_score_lines:
            x, y = zip(*power_score_line)
            ax_mean.plot(x, y, '-', color=color)
            annotate_idx = len(x) / 2
            ax_mean.annotate('%.2f' % power_score,
                             (x[annotate_idx], y[annotate_idx]),
                             horizontalalignment='right',
                             verticalalignment='top', xytext=(0, -10),
                             textcoords="offset pixels")

        power_summary = path.join(
            self.data_dir, 'pantheon_summary_power.png')
        ax_mean.set_title(self.expt_title +
                          '\nmean power scores of all runs by scheme',
                          fontsize=12)
        fig_mean.savefig(power_summary, dpi=300,
                         bbox_inches='tight', pad_inches=0.2)

    def run(self):
        self.eval_performance()

        if not self.no_graphs:
            self.plot_throughput_delay()


def main():
    args = parse_arguments(path.basename(__file__))

    plot = Plot(data_dir=args.data_dir,
                schemes=args.schemes,
                include_acklink=args.include_acklink,
                no_graphs=args.no_graphs)
    plot.run()


if __name__ == '__main__':
    main()
