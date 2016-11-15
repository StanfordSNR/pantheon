#!/usr/bin/env python

from os import path
from parse_arguments import parse_arguments


class PlotThroughputTime:
    def __init__(self, args):
        self.test_dir = path.abspath(path.dirname(__file__))
        self.src_dir = path.abspath(path.join(self.test_dir, '../src'))
        self.run_times = args.run_times
        self.cc_schemes = args.cc_schemes
        self.ms_per_bin = args.ms_per_bin

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
        pass


def main():
    args = parse_arguments(path.basename(__file__))

    plot_throughput_time = PlotThroughputTime(args)
    plot_throughput_time.plot_throughput_time()


if __name__ == '__main__':
    main()
