#!/usr/bin/env python

import sys
from os import path
import numpy as np
import project_root
import argparse
import matplotlib_agg
import matplotlib.pyplot as plt
import json
from helpers.helpers import parse_config, json_keys_as_num


def data_of_type(args, bandwidth, delay, perf_tput, perf_delay):
    normalized_tput = 100.0 * perf_tput / bandwidth

    if args.type == 'score':
        return np.log(normalized_tput) - np.log(perf_delay)
    elif args.type == 'tput':
        return normalized_tput
    elif args.type == 'delay':
        return perf_delay


def plot(args, data, bw_list, delay_list):
    all_schemes = parse_config()['schemes']

    if len(bw_list) == 1:
        fixed_bw = bw_list[0]
        x_data = delay_list
    elif len(delay_list) == 1:
        fixed_delay = delay_list[0]
        x_data = bw_list

    fig, ax = plt.subplots()

    for cc in data:
        y_data = []

        if len(bw_list) == 1:
            for delay in x_data:
                v = data_of_type(args, fixed_bw, delay,
                                 data[cc][fixed_bw][delay]['tput'],
                                 data[cc][fixed_bw][delay]['delay'])
                y_data.append(v)

        elif len(delay_list) == 1:
            for bw in x_data:
                v = data_of_type(args, bw, fixed_delay,
                                 data[cc][bw][fixed_delay]['tput'],
                                 data[cc][bw][fixed_delay]['delay'])
                y_data.append(v)

        if cc in all_schemes:
            friendly_cc_name = all_schemes[cc]['friendly_name']
            color = all_schemes[cc]['color']
            marker = all_schemes[cc]['marker']
        else:
            sys.exit('%s is not a scheme in src/config.yml' % cc)

        ax.plot(x_data, y_data, label=friendly_cc_name,
                color=color, marker=marker, markersize=3)

    # plot omniscient
    if args.type == 'score':
        if len(bw_list) == 1:
            y_data = [np.log(100.0) - np.log(delay) for delay in x_data]
        elif len(delay_list) == 1:
            y_data = [np.log(100.0) - np.log(fixed_delay)] * len(bw_list)

        ax.plot(x_data, y_data, label='omniscient', color='k')

    if len(bw_list) == 1:
        ax.set_xlabel('One-way propagation delay (ms)', fontsize=12)
        graph_path = path.join(
            args.output_dir,
            'mmdelay_%s_%smbps.svg' % (args.type, fixed_bw))
    elif len(delay_list) == 1:
        ax.set_xlabel('Link rate (Mbps)', fontsize=12)
        graph_path = path.join(
            args.output_dir,
            'linkrate_%s_%sms.svg' % (args.type, fixed_delay))

    if args.type == 'score':
        ax.set_ylabel('log(normalized throughput) - log(delay)', fontsize=12)
    elif args.type == 'tput':
        ax.set_ylabel('Normalized throughput (%)', fontsize=12)
    elif args.type == 'delay':
        ax.set_ylabel('95th percentile delay (ms)', fontsize=12)

    ax.grid()
    ax.set_xticks(x_data)

    fig_w, fig_h = fig.get_size_inches()
    fig.set_size_inches(0.8 * len(x_data), fig_h)

    lgd = ax.legend(bbox_to_anchor=(1, 0.5), loc='center left', fontsize=12)
    fig.savefig(graph_path, bbox_extra_artists=(lgd,),
                bbox_inches='tight', pad_inches=0.2)
    sys.stderr.write('Saved plot as %s\n' % graph_path)


def parse_data(args, bw_list, delay_list):
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

        for bw in bw_list:
            data[cc][bw] = {}
            for delay in delay_list:
                data[cc][bw][delay] = {}
                data[cc][bw][delay]['tput'] = cc_data[bw][delay]['tput']
                data[cc][bw][delay]['delay'] = cc_data[bw][delay]['delay']

    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--type',
            default='score', choices=['score', 'tput', 'delay'])
    parser.add_argument('--json-dir', metavar='DIR', required=True)
    parser.add_argument('--schemes', metavar='SCH1 SCH2...', required=True)
    parser.add_argument('--output-dir', metavar='DIR', default='.')
    parser.add_argument('--bandwidth', metavar='Mbps', required=True)
    parser.add_argument('--delay', metavar='ms', required=True)
    args = parser.parse_args()

    bw_list = sorted(map(int, args.bandwidth.split()))
    delay_list = sorted(map(int, args.delay.split()))

    if len(bw_list) == 1:
        sys.stderr.write('Fixing link rate and plotting mm-delay vs %s\n'
                         % args.type)
    elif len(delay_list) == 1:
        sys.stderr.write('Fixing mm-delay and plotting link rate vs %s\n'
                         % args.type)
    else:
        sys.exit('Either --bandwidth or --delay has to be a single value')

    data = parse_data(args, bw_list, delay_list)

    plot(args, data, bw_list, delay_list)


if __name__ == '__main__':
    main()
