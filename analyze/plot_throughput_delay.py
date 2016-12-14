#!/usr/bin/env python

import sys
import argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('ms_per_bin', metavar='ms-per-bin',
                        help='bin size (ms)')
    parser.add_argument('tunnel_log', metavar='tunnel-log',
                        help='tunnel log file')
    parser.add_argument(
        '--throughput-graph',
        metavar='OUTPUT-PATH',
        action='store',
        dest='throughput_graph',
        help='throughput graph to save')
    parser.add_argument(
        '--delay-graph',
        metavar='OUTPUT-PATH',
        action='store',
        dest='delay_graph',
        help='delay graph to save')

    args = parser.parse_args()

    if not args.throughput_graph or not args.delay_graph:
        sys.stderr.write('Must specify the path of output graphs\n')
        exit(1)

    return args


class TunnelPlot:
    def __init__(self, args):
        self.ms_per_bin = int(args.ms_per_bin)
        self.tunnel_log = args.tunnel_log
        self.throughput_graph = args.throughput_graph
        self.delay_graph = args.delay_graph

    def ms_to_bin(self, ts, first_ts):
        return (ts - first_ts) / self.ms_per_bin

    def bin_to_s(self, bin_id):
        return bin_id * self.ms_per_bin / 1000.0

    def parse_tunnel_log(self):
        tunlog = open(self.tunnel_log)

        self.flows = {}
        first_ts = None
        capacities = {}

        arrivals = {}
        departures = {}
        self.delays_t = {}
        self.delays = {}

        first_capacity = None
        last_capacity = None
        first_arrival = {}
        last_arrival = {}
        first_departure = {}
        last_departure = {}

        total_first_departure = None
        total_last_departure = None
        total_arrivals = 0
        total_departures = 0

        while True:
            line = tunlog.readline()
            if not line:
                break

            if line.startswith('#'):
                continue

            items = line.split()
            ts = int(items[0])
            event_type = items[1]
            num_bits = int(items[2]) * 8

            if first_ts is None:
                first_ts = ts

            bin_id = self.ms_to_bin(ts, first_ts)

            if event_type == '#':
                capacities[bin_id] = capacities.get(bin_id, 0) + num_bits

                if first_capacity is None:
                    first_capacity = ts

                if last_capacity is None or ts > last_capacity:
                    last_capacity = ts
            else:
                flow_id = int(items[-1])
                self.flows[flow_id] = True

                if event_type == '+':
                    if flow_id not in arrivals:
                        arrivals[flow_id] = {}
                        first_arrival[flow_id] = ts

                    if flow_id not in last_arrival:
                        last_arrival[flow_id] = ts
                    else:
                        if ts > last_arrival[flow_id]:
                            last_arrival[flow_id] = ts

                    old_value = arrivals[flow_id].get(bin_id, 0)
                    arrivals[flow_id][bin_id] = old_value + num_bits

                    total_arrivals += num_bits
                elif event_type == '-':
                    if flow_id not in departures:
                        departures[flow_id] = {}
                        first_departure[flow_id] = ts

                    if flow_id not in last_departure:
                        last_departure[flow_id] = ts
                    else:
                        if ts > last_departure[flow_id]:
                            last_departure[flow_id] = ts

                    old_value = departures[flow_id].get(bin_id, 0)
                    departures[flow_id][bin_id] = old_value + num_bits

                    # update total variables
                    if total_first_departure is None:
                        total_first_departure = ts
                    if (total_last_departure is None or
                            ts > total_last_departure):
                        total_last_departure = ts
                    total_departures += num_bits

                    # store delays in a list for each flow and sort later
                    delay = int(items[3])
                    if flow_id not in self.delays:
                        self.delays[flow_id] = []
                        self.delays_t[flow_id] = []
                    self.delays[flow_id].append(delay)
                    self.delays_t[flow_id].append(ts / 1000.0)

        tunlog.close()

        us_per_bin = 1000.0 * self.ms_per_bin

        # calculate average capacity
        self.avg_capacity = None
        if capacities:
            if last_capacity == first_capacity:
                self.avg_capacity = 0
            else:
                delta = last_capacity - first_capacity
                self.avg_capacity = sum(capacities.values()) / (1000.0 * delta)

        # transform capacities into a list
        self.link_capacity = []
        self.link_capacity_t = []
        capacity_bins = capacities.keys()
        for bin_id in xrange(min(capacity_bins), max(capacity_bins) + 1):
            self.link_capacity.append(capacities.get(bin_id, 0) / us_per_bin)
            self.link_capacity_t.append(self.bin_to_s(bin_id))

        # calculate ingress and egress throughput for each flow
        self.ingress_tput = {}
        self.egress_tput = {}
        self.ingress_t = {}
        self.egress_t = {}
        self.avg_ingress = {}
        self.avg_egress = {}
        self.percentile_delay = {}
        self.loss_rate = {}

        total_delays = []

        for flow_id in self.flows:
            # calculate average ingress and egress throughput
            first_arrival_ts = first_arrival.get(flow_id, None)
            last_arrival_ts = last_arrival.get(flow_id, None)

            # update variables for all flows
            if last_arrival_ts == first_arrival_ts:
                self.avg_ingress[flow_id] = 0
            else:
                delta = last_arrival_ts - first_arrival_ts
                flow_arrivals = sum(arrivals.get(flow_id, {}).values())
                self.avg_ingress[flow_id] = flow_arrivals / (1000.0 * delta)

            first_departure_ts = first_departure.get(flow_id, None)
            last_departure_ts = last_departure.get(flow_id, None)
            if last_departure_ts == first_departure_ts:
                self.avg_egress[flow_id] = 0
            else:
                delta = last_departure_ts - first_departure_ts
                flow_departures = sum(departures.get(flow_id, {}).values())
                self.avg_egress[flow_id] = flow_departures / (1000.0 * delta)

            self.ingress_tput[flow_id] = []
            self.egress_tput[flow_id] = []
            self.ingress_t[flow_id] = []
            self.egress_t[flow_id] = []

            ingress_bins = arrivals[flow_id].keys()
            for bin_id in xrange(min(ingress_bins), max(ingress_bins) + 1):
                self.ingress_tput[flow_id].append(
                        arrivals[flow_id].get(bin_id, 0) / us_per_bin)
                self.ingress_t[flow_id].append(self.bin_to_s(bin_id))

            egress_bins = departures[flow_id].keys()
            for bin_id in xrange(min(egress_bins), max(egress_bins) + 1):
                self.egress_tput[flow_id].append(
                        departures[flow_id].get(bin_id, 0) / us_per_bin)
                self.egress_t[flow_id].append(self.bin_to_s(bin_id))

            # calculate 95th percentile per-packet one-way delay
            self.percentile_delay[flow_id] = np.percentile(
                    self.delays[flow_id], 95)
            total_delays += self.delays[flow_id]

            # calculate loss rate for each flow
            flow_arrivals = sum(arrivals.get(flow_id, {}).values())
            flow_departures = sum(departures.get(flow_id, {}).values())
            self.loss_rate[flow_id] = 1 - 1.0 * flow_departures / flow_arrivals

        self.total_loss_rate = 1 - 1.0 * total_departures / total_arrivals
        # calculate total average throughput and 95th percentile delay
        if total_last_departure == total_first_departure:
            self.total_avg_egress = 0
        else:
            delta = total_last_departure - total_first_departure
            self.total_avg_egress = total_departures / (1000.0 * delta)

        self.total_percentile_delay = np.percentile(total_delays, 95)

    def plot_throughput_graph(self):
        fig, ax = plt.subplots()

        if self.link_capacity:
            ax.fill_between(self.link_capacity_t, 0, self.link_capacity,
                            facecolor='linen')

        for flow_id in self.flows:
            ax.plot(self.ingress_t[flow_id], self.ingress_tput[flow_id],
                    label='Flow %s ingress (mean %.2f Mbit/s)'
                    % (flow_id, self.avg_ingress[flow_id]))
            ax.plot(self.egress_t[flow_id], self.egress_tput[flow_id],
                    label='Flow %s egress (mean %.2f Mbit/s)'
                    % (flow_id, self.avg_egress[flow_id]))

        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Throughput (Mbit/s)')

        if self.link_capacity:
            ax.set_title('Average capacity %.2f Mbit/s (shaded region)'
                         % self.avg_capacity)

        ax.grid()
        lgd = ax.legend(scatterpoints=1, bbox_to_anchor=(0.5, -0.26),
                        loc='lower center', ncol=2, fontsize=12)

        (fig_w, fig_h) = fig.get_size_inches()
        self.tmin, self.tmax = ax.get_xlim()
        fig.set_size_inches((self.tmax - self.tmin) * 0.7, fig_h)

        fig.savefig(self.throughput_graph, bbox_extra_artists=(lgd,),
                    bbox_inches='tight', pad_inches=0.2)

    def plot_delay_graph(self):
        fig, ax = plt.subplots()

        colors = ['r', 'y', 'b', 'g', 'c', 'm']
        color_i = 0
        for flow_id in self.flows:
            color = colors[color_i]
            ax.scatter(self.delays_t[flow_id], self.delays[flow_id],
                       color=color, marker='.', s=1,
                       label='Flow %s (95th percentile %.0f ms)'
                       % (flow_id, self.percentile_delay[flow_id]))

            color_i += 1
            if color_i == len(colors):
                color_i = 0

        ax.set_xlabel('Time (s)')
        ax.set_ylabel('One-way delay (ms)')
        ax.grid()
        lgd = ax.legend(scatterpoints=1, bbox_to_anchor=(0.5, -0.2),
                        loc='lower center', ncol=2, fontsize=12)

        ax.set_xlim(self.tmin, self.tmax)
        (fig_w, fig_h) = fig.get_size_inches()
        fig.set_size_inches((self.tmax - self.tmin) * 0.7, fig_h)

        fig.savefig(self.delay_graph, bbox_extra_artists=(lgd,),
                    bbox_inches='tight', pad_inches=0.2)

    def print_statistics(self):
        sys.stderr.write('-- Total:\n')
        if self.avg_capacity is not None:
            sys.stderr.write('Average capacity: %.2f Mbit/s\n'
                             % self.avg_capacity)

        sys.stderr.write('Average throughput: %.2f Mbit/s'
                         % self.total_avg_egress)

        if self.avg_capacity is not None:
            sys.stderr.write(' (%.1f%% utilization)' % (
                100.0 * self.total_avg_egress / self.avg_capacity))
        sys.stderr.write('\n')

        sys.stderr.write('95th percentile per-packet one-way delay: '
                         '%.0f ms\n' % self.total_percentile_delay)
        sys.stderr.write('Loss rate: %.2f%%\n'
                         % (self.total_loss_rate * 100.0))

        for flow_id in self.flows:
            sys.stderr.write('-- Flow %s:\n' % flow_id)
            sys.stderr.write('Average throughput: %.2f Mbit/s\n'
                             % self.avg_egress[flow_id])
            sys.stderr.write('95th percentile per-packet one-way delay: '
                             '%.0f ms\n' % self.percentile_delay[flow_id])
            sys.stderr.write('Loss rate: %.2f%%\n'
                             % (self.loss_rate[flow_id] * 100.0))

    def tunnel_plot(self):
        self.parse_tunnel_log()
        self.plot_throughput_graph()
        self.plot_delay_graph()
        self.print_statistics()


def main():
    args = parse_arguments()

    tunnel_plot = TunnelPlot(args)
    tunnel_plot.tunnel_plot()


if __name__ == '__main__':
    main()
