#!/usr/bin/env python

import matplotlib
matplotlib.use('Agg')

import sys
from os import path
import numpy as np
import argparse
import matplotlib.pyplot as plt


def interp_num(n):
    try:
        n = float(n)
        return int(n) if n.is_integer() else n
    except ValueError:
        return n


def json_keys_as_num(json_obj):
    if isinstance(json_obj):
        return {interp_num(k): v for k, v in json_obj.iteritems()}
    else:
        return json_obj


def plot(args, data, bw_range, delay):
    """ Plots various graphs, each on fixed delay given a dictionary as such:
        {scheme: {data}}

    data dictionary is as such:
        {bw: delay: {'tput': X, 'delay': Y, 'loss': Z}}

    Each data dictionary is sorted by bandwidth and delay.
    """

    output_dir = args.json_dir if args.output_dir is None else args.output_dir

    fig, ax = plt.subplots()
    colors = ['b', 'g', 'r', 'y', 'c', 'm', 'k']
    color_i = 0

    for cc in data:
        x_data = []
        y_data = []

        sorted_bw_list = sorted(data[cc].keys())
        for bw in sorted_bw_list:
            x_data.append(bw)

            normalized_tput = 100.0 * data[cc][bw][delay]['tput'] / bw
            seen_delay = data[cc][bw][delay]['delay']

            if args.type == 'score':
                y_data.append(np.log(normalized_tput) - np.log(seen_delay))
            elif args.type == 'tput':
                y_data.append(normalized_tput)
            elif args.type == 'delay':
                y_data.append(seen_delay)

        color = colors[color_i]
        ax.plot(x_data, y_data, label=cc, color=color)

        color_i += 1
        if color_i == len(colors):
            color_i = 0

    # plot omniscient
    if args.type == 'score':
        x_data = bw_range
        y_data = [np.log(100.0) - np.log(delay)] * len(x_data)
        ax.plot(x_data, y_data, label='omniscient', color='k')

    ax.set_xlabel('Link speed (Mbps)', fontsize=12)

    if args.type == 'score':
        ax.set_ylabel('log(normalized throughput) - log(delay)', fontsize=12)

        plot_path = path.join(output_dir, 'linkspeed_score_%s_delay.png' %
                             (delay))
    elif args.type == 'tput':
        ax.set_ylabel('Normalized throughput (%)', fontsize=12)

        plot_path = path.join(output_dir, 'linkspeed_tput_%s_delay.png' %
                             (delay))
    elif args.type == 'delay':
        ax.set_ylabel('Delay (ms)', fontsize=12)

        plot_path = path.join(output_dir, 'linkspeed_delay_%s_delay.png' %
                             (delay))

    ax.grid()
    ax.set_xticks(x_data)

    lgd = ax.legend(bbox_to_anchor=(1, 0.5), loc='center left', fontsize=12)
    fig.savefig(plot_path, dpi=300, bbox_extra_artists=(lgd,),
                bbox_inches='tight', pad_inches=0.2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--type',
            default='score', choices=['score', 'tput', 'delay'])
    parser.add_argument('--fix_param',      # TODO implement this
            default='delay', choices=['bw', 'delay'])
    parser.add_argument('--json-dir', metavar='DIR', required=True)
    parser.add_argument('--output-dir', metavar='DIR')
    parser.add_argument('--schemes', metavar='SCH1 SCH2...', required=True)

    args = parser.parse_args()
    schemes = args.schemes.split()
    json_dir = args.json_dir

    data = {}
    bandwidths = set()
    delays = set()

    for cc in schemes:
        json_name = '%s.json' % cc
        json_path = path.join(json_dir, json_name)

        if not path.isfile(json_path):
            sys.exit('%s does not exist!' % json_path)

        with open(json_path) as json_file:
            data[cc] = json.load(json_file, object_hook=json_keys_as_num)
            bandwidths |= set(data[cc].keys())
            for bw in data[cc]:
                delays |= set(data[cc][bw].keys())

    bw_range = sorted(list(bandwidths))
    delay_range = sorted(list(delays))

    for delay in delay_range:
        plot(args, data, bw_range, delay)


if __name__ == '__main__':
    main()
