#!/usr/bin/env python

from os import path
import sys
import math
import multiprocessing
from multiprocessing.pool import ThreadPool
import numpy as np
import matplotlib_agg
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from parse_arguments import parse_arguments
from analyze_helpers import load_test_metadata, verify_schemes_with_meta
from helpers.helpers import parse_config, print_cmd, utc_time
import tunnel_graph


class Plot(object):
    def __init__(self, args):
        self.data_dir = path.abspath(args.data_dir)
        self.include_acklink = args.include_acklink
        self.no_graphs = args.no_graphs

        metadata_path = path.join(self.data_dir, 'pantheon_metadata.json')
        meta = load_test_metadata(metadata_path)
        self.cc_schemes = verify_schemes_with_meta(args.schemes, meta)

        self.run_times = meta['run_times']
        self.flows = meta['flows']
        self.runtime = meta['runtime']
        self.expt_title = self.generate_expt_title(meta)

    def generate_expt_title(self, meta):
        if meta['mode'] == 'local':
            expt_title = 'local test in mahimahi, '
        elif meta['mode'] == 'remote':
            txt = {}
            for side in ['local', 'remote']:
                txt[side] = []

                if '%s_desc' % side in meta:
                    txt[side].append(meta['%s_desc' % side])
                else:
                    txt[side].append(side)

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

        runs_str = 'run' if meta['run_times'] == 1 else 'runs'
        expt_title += '%s %s of %ss each per scheme\n' % (
            meta['run_times'], runs_str, meta['runtime'])

        if meta['flows'] > 1:
            expt_title += '%s flows with %ss interval between flows' % (
                meta['flows'], meta['interval'])

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

                if duration < 0.8 * self.runtime:
                    sys.stderr.write(
                        'Warning: "tunnel_graph %s" had duration %.2f seconds '
                        'but should have been around %s seconds. Ignoring this'
                        ' run.\n' % (log_path, duration, self.runtime))
                    error = True

        if error:
            return (None, None, None, None)

        return (tput, delay, loss, stats)

    def update_stats_log(self, cc, run_id, stats):
        stats_log_path = path.join(
            self.data_dir, '%s_stats_run%s.log' % (cc, run_id))

        if not path.isfile(stats_log_path):
            sys.stderr.write('Warning: %s does not exist\n' % stats_log_path)
            return None

        saved_lines = ''

        # back up old stats logs
        with open(stats_log_path) as stats_log:
            for line in stats_log:
                if any([x in line for x in [
                        'Start at:', 'End at:', 'clock offset:']]):
                    saved_lines += line
                else:
                    continue

        # write to new stats log
        with open(stats_log_path, 'w') as stats_log:
            stats_log.write(saved_lines)

            if stats:
                stats_log.write('\n# Below is generated by %s at %s\n' %
                                (path.basename(__file__), utc_time()))
                stats_log.write('# Datalink statistics\n')
                stats_log.write('%s' % stats)

    def eval_performance(self):
        data = {}

        results = {}
        for cc in self.cc_schemes:
            data[cc] = []
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
                self.update_stats_log(cc, run_id, stats)

                if tput is None or delay is None:
                    continue

                data[cc].append((tput, delay, loss))

        sys.stderr.write('Appended datalink statistics to stats files in %s\n'
                         % self.data_dir)
        return data

    def xaxis_log_scale(self, ax, min_delay, max_delay):
        if min_delay < -2:
            x_min = int(-math.pow(2, math.ceil(math.log(-min_delay, 2))))
        elif min_delay < 0:
            x_min = -2
        elif min_delay < 2:
            x_min = 0
        else:
            x_min = int(math.pow(2, math.floor(math.log(min_delay, 2))))

        if max_delay < -2:
            x_max = int(-math.pow(2, math.floor(math.log(-max_delay, 2))))
        elif max_delay < 0:
            x_max = 0
        elif max_delay < 2:
            x_max = 2
        else:
            x_max = int(math.pow(2, math.ceil(math.log(max_delay, 2))))

        symlog = False
        if x_min <= -2:
            if x_max >= 2:
                symlog = True
        elif x_min == 0:
            if x_max >= 8:
                symlog = True
        elif x_min >= 2:
            if x_max > 4 * x_min:
                symlog = True

        if symlog:
            ax.set_xscale('symlog', basex=2, linthreshx=2, linscalex=0.5)
            ax.set_xlim(x_min, x_max)
            ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))

    def plot_throughput_delay(self, data):
        min_raw_delay = sys.maxint
        min_mean_delay = sys.maxint
        max_raw_delay = -sys.maxint
        max_mean_delay = -sys.maxint

        fig_raw, ax_raw = plt.subplots()
        fig_mean, ax_mean = plt.subplots()

        schemes_config = parse_config()['schemes']
        for cc in data:
            if not data[cc]:
                continue

            value = data[cc]
            cc_name = schemes_config[cc]['friendly_name']
            color = schemes_config[cc]['color']
            marker = schemes_config[cc]['marker']
            y_data, x_data, _ = zip(*value)

            # update min and max raw delay
            min_raw_delay = min(min(x_data), min_raw_delay)
            max_raw_delay = max(max(x_data), max_raw_delay)

            # plot raw values
            ax_raw.scatter(x_data, y_data, color=color, marker=marker,
                           label=cc_name, clip_on=False)

            # plot the average of raw values
            x_mean = np.mean(x_data)
            y_mean = np.mean(y_data)

            # update min and max mean delay
            min_mean_delay = min(x_mean, min_mean_delay)
            max_mean_delay = max(x_mean, max_mean_delay)

            ax_mean.scatter(x_mean, y_mean, color=color, marker=marker,
                            clip_on=False)
            ax_mean.annotate(cc_name, (x_mean, y_mean))

        for fig_type, fig, ax in [('raw', fig_raw, ax_raw),
                                  ('mean', fig_mean, ax_mean)]:
            if fig_type == 'raw':
                self.xaxis_log_scale(ax, min_raw_delay, max_raw_delay)
            else:
                self.xaxis_log_scale(ax, min_mean_delay, max_mean_delay)
            ax.invert_xaxis()

            yticks = ax.get_yticks()
            if yticks[0] < 0:
                ax.set_ylim(bottom=0)

            xlabel = '95th percentile one-way delay (ms)'
            ax.set_xlabel(xlabel, fontsize=12)
            ax.set_ylabel('Average throughput (Mbit/s)', fontsize=12)
            ax.grid()

        # save pantheon_summary.png
        ax_raw.set_title(self.expt_title.strip(), y=1.02, fontsize=12)
        lgd = ax_raw.legend(scatterpoints=1, bbox_to_anchor=(1, 0.5),
                            loc='center left', fontsize=12)
        raw_summary = path.join(self.data_dir, 'pantheon_summary.png')
        fig_raw.savefig(raw_summary, dpi=300, bbox_extra_artists=(lgd,),
                        bbox_inches='tight', pad_inches=0.2)

        # save pantheon_summary_mean.png
        ax_mean.set_title(self.expt_title +
                          ' (mean of all runs by scheme)', fontsize=12)
        mean_summary = path.join(
            self.data_dir, 'pantheon_summary_mean.png')
        fig_mean.savefig(mean_summary, dpi=300,
                         bbox_inches='tight', pad_inches=0.2)

        sys.stderr.write(
            'Saved throughput graphs, delay graphs, and summary '
            'graphs in %s\n' % self.data_dir)

    def run(self):
        data = self.eval_performance()

        if not self.no_graphs:
            self.plot_throughput_delay(data)


def main():
    args = parse_arguments(path.basename(__file__))
    Plot(args).run()


if __name__ == '__main__':
    main()
