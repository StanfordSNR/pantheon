#!/usr/bin/env python

import math
import time
from os import path
import pantheon_helpers
from helpers.parse_arguments import parse_arguments
from helpers.pantheon_help import get_friendly_names

import matplotlib_agg
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


class PlotThroughputTime:
    def __init__(self, analysis_dir, metadata_dict, ms_per_bin):
        self.analysis_dir = analysis_dir
        self.src_dir = path.abspath(path.join(self.analysis_dir, '../src'))
        self.run_times = metadata_dict['run_times']
        self.cc_schemes = metadata_dict['cc_schemes'].split()
        self.ms_per_bin = ms_per_bin

    def ms_to_bin(self, ts, flow_base_ts):
        return (ts - flow_base_ts) / self.ms_per_bin

    def parse_tunnel_log(self, tunnel_log_path):
        tunlog = open(tunnel_log_path)

        # read init timestamp
        init_ts = None
        while not init_ts:
            line = tunlog.readline()
            if 'init timestamp' in line:
                init_ts = int(line.split(':')[1])
        assert init_ts

        flow_base_ts = {}  # timestamp when each flow sent the first byte
        departures = {}  # number of bits leaving the tunnel within a bin

        while True:
            line = tunlog.readline()
            if not line:
                break

            if '#' in line:
                continue

            items = line.split()
            event_type = items[1]
            assert event_type == '+' or event_type == '-'

            ts = int(items[0])
            num_bits = int(items[2]) * 8
            flow_id = int(items[-1])

            if event_type == '+':
                if flow_id not in flow_base_ts:
                    flow_base_ts[flow_id] = ts
            else:
                if flow_id not in departures:
                    departures[flow_id] = {}
                else:
                    assert flow_id in flow_base_ts
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

    def plot_throughput_time(self):
        friendly_names = get_friendly_names(self.cc_schemes)

        fig, ax = plt.subplots()
        total_min_time = None
        total_max_time = None
        for cc in self.cc_schemes:
            cc_name = friendly_names[cc]

            for run_id in xrange(1, self.run_times + 1):
                tunnel_log_path = path.join(
                    self.analysis_dir, '%s_datalink_run%s.log' % (cc, run_id))
                clock_time, throughput = self.parse_tunnel_log(tunnel_log_path)

                min_time = None
                max_time = None
                max_tput = None

                for flow_id in clock_time:
                    ax.plot(clock_time[flow_id], throughput[flow_id])

                    if not min_time or clock_time[flow_id][0] < min_time:
                        min_time = clock_time[flow_id][0]
                    if not max_time or clock_time[flow_id][-1] < min_time:
                        max_time = clock_time[flow_id][-1]
                    flow_max_tput = max(throughput[flow_id])
                    if not max_tput or flow_max_tput > max_tput:
                        max_tput = flow_max_tput

                ax.annotate(cc_name, (min_time, max_tput))

                if not total_min_time or min_time < total_min_time:
                    total_min_time = min_time
                if not total_max_time or max_time > total_max_time:
                    total_max_time = max_time

        xmin = int(math.floor(total_min_time))
        xmax = int(math.ceil(total_max_time))
        ax.set_xlim(xmin, xmax)

        new_xticks = range(xmin, xmax, 10)
        ax.set_xticks(new_xticks)
        formatter = ticker.FuncFormatter(lambda x, pos: x - xmin)
        ax.xaxis.set_major_formatter(formatter)

        (fig_w, fig_h) = fig.get_size_inches()
        fig.set_size_inches(len(new_xticks), fig_h)

        start_datetime = time.strftime('%a, %d %b %Y %H:%M:%S',
                                       time.localtime(total_min_time))
        start_datetime += ' ' + time.strftime('%z')
        ax.set_xlabel('Time (s) since ' + start_datetime)
        ax.set_ylabel('Throughput (Mbit/s)')

        fig_path = path.join(self.analysis_dir, 'pantheon_throughput_time.png')
        fig.savefig(fig_path, bbox_inches='tight', pad_inches=0.2)


def main():
    args = parse_arguments(path.basename(__file__))
    analysis_dir = path.abspath(path.dirname(__file__))
    # load pantheon_metadata.json as a dictionary
    metadata_fname = path.join(analysis_dir, 'pantheon_metadata.json')
    with open(metadata_fname) as metadata_file:
        metadata_dict = json.load(metadata_file)

    plot_throughput_time = PlotThroughputTime(analysis_dir, metadata_dict,
                                              args.ms_per_bin)
    plot_throughput_time.plot_throughput_time()


if __name__ == '__main__':
    main()
