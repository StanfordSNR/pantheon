#!/usr/bin/env python

from os import path
import sys
import math
import json
import argparse
import numpy as np
import matplotlib_agg
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import project_root
from helpers.helpers import parse_config, json_keys_as_num


def plot(args, data):
    schemes_config = parse_config()['schemes']

    fig, ax = plt.subplots()

    for cc in data:
        if not data[cc]:
            sys.stderr.write('No performance data for scheme %s\n' % cc)
            continue

        cc_name = schemes_config[cc]['friendly_name']
        color = schemes_config[cc]['color']
        marker = schemes_config[cc]['marker']

        x_data = data[cc]['delay']
        y_data = data[cc]['tput']
        ax.scatter(x_data, y_data, color=color, marker=marker)
        ax.annotate(cc_name, (x_data, y_data))

    ax.set_xscale('log', basex=2)
    ax.set_ylim(0, int(args.bandwidth))
    #ax.set_xlim(min, max)
    #ax.set_xticks([50, 80, 150, 200, 256, 512])
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
    ax.invert_xaxis()

    ax.set_xlabel('95th percentile one-way delay (ms)', fontsize=12)
    ax.set_ylabel('Average throughput (Mbit/s)', fontsize=12)
    ax.grid()

    if args.graph_name is None:
        emu_graph = path.join(args.output_dir,
            'emu_perf_%smbps_%sms.svg' % (args.bandwidth, args.delay))
    else:
        emu_graph = path.join(args.output_dir, args.graph_name)

    fig.savefig(emu_graph, bbox_inches='tight', pad_inches=0.2)

    sys.stderr.write('Saved plot as %s\n' % emu_graph)


def parse_data(args):
    # bandwidth and delay to plot
    bw = args.bandwidth
    delay = args.delay

    schemes = args.schemes.split()
    data = {}

    for cc in schemes:
        data[cc] = {}

        json_name = '%s.json' % cc
        json_path = path.join(args.json_dir, json_name)

        if not path.isfile(json_path):
            sys.exit('%s does not exist!' % json_path)

        with open(json_path) as json_file:
            cc_data = json.load(json_file, object_hook=json_keys_as_num)

        data[cc]['tput'] = cc_data[bw][delay]['tput']
        data[cc]['delay'] = cc_data[bw][delay]['delay']

    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--json-dir', metavar='DIR', required=True)
    parser.add_argument('--schemes', metavar='SCH1 SCH2...', required=True)
    parser.add_argument('--output-dir', metavar='DIR', default='.')
    parser.add_argument('--graph-name')
    parser.add_argument('--bandwidth', metavar='Mbps', type=int, required=True)
    parser.add_argument('--delay', metavar='ms', type=int, required=True)
    args = parser.parse_args()

    data = parse_data(args)

    plot(args, data)


if __name__ == '__main__':
    main()
