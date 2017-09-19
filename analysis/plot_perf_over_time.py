#!/usr/bin/env python

import sys
from os import path
import json
import argparse
import project_root
from helpers.helpers import parse_config

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def parse_data(args):
    json_path = args.json_data

    if not path.isfile(json_path):
        sys.exit('%s does not exist!' % json_path)

    data = {}
    with open(json_path) as f:
        link_data = json.load(f)

        dates = sorted(link_data.keys())
        for date in dates:
            data[date] = {}

            for cc in link_data[date]:
                if cc not in data[date]:
                    data[date][cc] = {}
                data[date][cc]['tput'] = link_data[date][cc]['avg_tput']
                data[date][cc]['delay'] = link_data[date][cc]['avg_delay']

    return data, dates


def plot(args, data, dates):
    all_schemes = parse_config()['schemes']

    cc_to_plot = [
        'bbr', 'default_tcp', 'ledbat', 'pcc', 'quic', 'scream',
        'sprout', 'taova', 'vegas', 'verus', 'webrtc']

    fig, ax = plt.subplots()

    x_data = range(len(dates))

    for cc in cc_to_plot:
        y_data = []

        for date in dates:
            y_data.append(float(data[date][cc][args.type]))

        friendly_cc_name = all_schemes[cc]['friendly_name']
        color = all_schemes[cc]['color']
        marker = all_schemes[cc]['marker']

        ax.plot(x_data, y_data, label=friendly_cc_name,
                color=color, marker=marker, markersize=3)

    filename_prefix = path.basename(args.json_data)
    filename_prefix = filename_prefix.split('.')[0]
    filename_prefix = filename_prefix.lower().replace('-', '_')

    if args.type == 'tput':
        ax.set_ylabel('mean of average throughput (Mbps)', fontsize=12)
        plot_path = path.join(args.output_dir,
                              '%s_tput_over_time.pdf' % filename_prefix)
    elif args.type == 'delay':
        ax.set_ylabel('mean of 95th percentile delay (ms)', fontsize=12)
        plot_path = path.join(args.output_dir,
                              '%s_delay_over_time.pdf' % filename_prefix)

    ax.grid()
    ax.set_xticks(x_data)

    x_tick_labels = [date.split('T')[0] for date in dates]
    ax.set_xticklabels(sorted(x_tick_labels), rotation=10)

    fig_w, fig_h = fig.get_size_inches()
    fig.set_size_inches(1.2 * len(x_data), fig_h)

    lgd = ax.legend(bbox_to_anchor=(1, 0.5), loc='center left', fontsize=12)
    fig.savefig(plot_path, dpi=300, bbox_extra_artists=(lgd,),
                bbox_inches='tight', pad_inches=0.2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--json-data', metavar='JSON', required=True,
                        help='JSON data containing performance over time')
    parser.add_argument('--output-dir', metavar='DIR', required=True)
    parser.add_argument('--type', required=True, choices=['tput', 'delay'])
    args = parser.parse_args()

    data, dates = parse_data(args)
    plot(args, data, dates)


if __name__ == '__main__':
    main()
