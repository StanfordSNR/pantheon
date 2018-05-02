#!/usr/bin/env python

import sys
from os import path
import math
import time
import matplotlib_agg
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import arg_parser
import context
from helpers import utils


class PlotThroughputTime(object):
    def __init__(self, args):
        self.data_dir = path.abspath(args.data_dir)
        self.ms_per_bin = args.ms_per_bin
        self.amplify = args.amplify

        metadata_path = path.join(self.data_dir, 'pantheon_metadata.json')
        meta = utils.load_test_metadata(metadata_path)
        self.cc_schemes = utils.verify_schemes_with_meta(args.schemes, meta)

        self.run_times = meta['run_times']
        self.flows = meta['flows']

    def ms_to_bin(self, ts, flow_base_ts):
        return int((ts - flow_base_ts) / self.ms_per_bin)

    def parse_tunnel_log(self, tunnel_log_path):
        tunlog = open(tunnel_log_path)

        # read init timestamp
        init_ts = None
        while init_ts is None:
            line = tunlog.readline()
            if 'init timestamp' in line:
                init_ts = float(line.split(':')[1])

        flow_base_ts = {}  # timestamp when each flow sent the first byte
        departures = {}  # number of bits leaving the tunnel within a bin

        while True:
            line = tunlog.readline()
            if not line:
                break

            if '#' in line:
                continue

            items = line.split()
            ts = float(items[0])
            event_type = items[1]
            num_bits = int(items[2]) * 8

            if event_type == '+':
                if len(items) == 4:
                    flow_id = int(items[-1])
                else:
                    flow_id = 0

                if flow_id not in flow_base_ts:
                    flow_base_ts[flow_id] = ts
            elif event_type == '-':
                if len(items) == 5:
                    flow_id = int(items[-1])
                else:
                    flow_id = 0

                if flow_id not in departures:
                    departures[flow_id] = {}
                else:
                    bin_id = self.ms_to_bin(ts, flow_base_ts[flow_id])
                    old_value = departures[flow_id].get(bin_id, 0)
                    departures[flow_id][bin_id] = old_value + num_bits

        tunlog.close()

        # prepare return values
        us_per_bin = 1000.0 * self.ms_per_bin
        clock_time = {}  # data for x-axis
        throughput = {}  # data for y-axis
        for flow_id in departures:
            start_ts = flow_base_ts[flow_id] + init_ts + self.ms_per_bin / 2.0
            clock_time[flow_id] = []
            throughput[flow_id] = []

            max_bin_id = max(departures[flow_id].keys())
            for bin_id in xrange(0, max_bin_id + 1):
                time_sec = (start_ts + bin_id * self.ms_per_bin) / 1000.0
                clock_time[flow_id].append(time_sec)

                tput_mbps = departures[flow_id].get(bin_id, 0) / us_per_bin
                throughput[flow_id].append(tput_mbps)

        return clock_time, throughput

    def run(self):
        fig, ax = plt.subplots()
        total_min_time = None
        total_max_time = None

        if self.flows > 0:
            datalink_fmt_str = '%s_datalink_run%s.log'
        else:
            datalink_fmt_str = '%s_mm_datalink_run%s.log'

        schemes_config = utils.parse_config()['schemes']
        for cc in self.cc_schemes:
            cc_name = schemes_config[cc]['name']

            for run_id in xrange(1, self.run_times + 1):
                tunnel_log_path = path.join(
                    self.data_dir, datalink_fmt_str % (cc, run_id))
                clock_time, throughput = self.parse_tunnel_log(tunnel_log_path)

                min_time = None
                max_time = None
                max_tput = None

                for flow_id in clock_time:
                    ax.plot(clock_time[flow_id], throughput[flow_id])

                    if min_time is None or clock_time[flow_id][0] < min_time:
                        min_time = clock_time[flow_id][0]
                    if max_time is None or clock_time[flow_id][-1] < min_time:
                        max_time = clock_time[flow_id][-1]
                    flow_max_tput = max(throughput[flow_id])
                    if max_tput is None or flow_max_tput > max_tput:
                        max_tput = flow_max_tput

                ax.annotate(cc_name, (min_time, max_tput))

                if total_min_time is None or min_time < total_min_time:
                    total_min_time = min_time
                if total_max_time is None or max_time > total_max_time:
                    total_max_time = max_time

        xmin = int(math.floor(total_min_time))
        xmax = int(math.ceil(total_max_time))
        ax.set_xlim(xmin, xmax)

        new_xticks = range(xmin, xmax, 10)
        ax.set_xticks(new_xticks)
        formatter = ticker.FuncFormatter(lambda x, pos: x - xmin)
        ax.xaxis.set_major_formatter(formatter)

        fig_w, fig_h = fig.get_size_inches()
        fig.set_size_inches(self.amplify * len(new_xticks), fig_h)

        start_datetime = time.strftime('%a, %d %b %Y %H:%M:%S',
                                       time.localtime(total_min_time))
        start_datetime += ' ' + time.strftime('%z')
        ax.set_xlabel('Time (s) since ' + start_datetime, fontsize=12)
        ax.set_ylabel('Throughput (Mbit/s)', fontsize=12)

        for graph_format in ['svg', 'pdf']:
            fig_path = path.join(
                self.data_dir, 'pantheon_throughput_time.%s' % graph_format)
            fig.savefig(fig_path, bbox_inches='tight', pad_inches=0.2)

        sys.stderr.write(
            'Saved pantheon_throughput_time in %s\n' % self.data_dir)

        plt.close('all')


def main():
    args = arg_parser.parse_over_time()
    PlotThroughputTime(args).run()


if __name__ == '__main__':
    main()
