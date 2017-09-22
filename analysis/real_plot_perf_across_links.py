#!/usr/bin/env python

import sys
from os import path
import json
import argparse
import numpy as np
import project_root
from helpers.helpers import parse_config

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def calculate_mean(link_data):
    mean_data = {}

    for date in link_data:
        perf_data = link_data[date]['data']

        for cc in perf_data:
            if cc not in mean_data:
                mean_data[cc] = {}
                mean_data[cc]['tput'] = []
                mean_data[cc]['delay'] = []

            mean_data[cc]['tput'].append(float(perf_data[cc]['tput']))
            mean_data[cc]['delay'].append(float(perf_data[cc]['delay']))

    for cc in mean_data:
        mean_data[cc]['tput'] = np.mean(mean_data[cc]['tput'])
        mean_data[cc]['delay'] = np.mean(mean_data[cc]['delay'])

    return mean_data


def parse_data(args):
    data_dir = args.data_dir

    peer_server = {
        'Stanford': 'AWS California',
        'Mexico': 'AWS California',
        'Brazil': 'AWS Brazil',
        'Colombia': 'AWS Brazil',
        'India': 'AWS India',
        'China': 'AWS Korea',
    }

    data = {}
    x_tick_labels = []

    for node_key in peer_server:
        server = peer_server[node_key]

        if args.link_type == 'cell':
            node = node_key + ' ppp0'
        else:
            node = node_key

        for to_node in [True, False]:
            if to_node:
                link = '%s to %s' % (server, node)
                x_tick_labels.append('%s (down)' % node)
            else:
                link = '%s to %s' % (node, server)
                x_tick_labels.append('%s (up)' % node)

            json_name = '%s.json' % link.replace(' ', '-')
            json_path = path.join(data_dir, json_name)

            if not path.isfile(json_path):
                sys.exit('%s does not exist!' % json_path)

            with open(json_path) as f:
                link_data = json.load(f)
                for date in link_data:
                    data[link] = calculate_mean(link_data)

    return data, x_tick_labels


def plot(args, data, x_tick_labels):
    all_schemes = parse_config()['schemes']

    cc_to_plot = [
        'bbr', 'default_tcp', 'ledbat', 'pcc', 'quic', 'scream',
        'sprout', 'taova', 'vegas', 'verus', 'webrtc']

    fig, ax = plt.subplots()

    links = data.keys()
    x_data = range(len(links))

    for cc in cc_to_plot:
        y_data = []

        for link in links:
            y_data.append(float(data[link][cc][args.type]))

        friendly_cc_name = all_schemes[cc]['friendly_name']
        color = all_schemes[cc]['color']
        marker = all_schemes[cc]['marker']

        ax.plot(x_data, y_data, label=friendly_cc_name,
                color=color, marker=marker, markersize=3)

    if args.type == 'tput':
        ax.set_ylabel('throughput / highest throughput', fontsize=12)

        if args.link_type == 'eth':
            plot_path = path.join(args.output_dir, 'tput_across_links.pdf')
        elif args.link_type == 'cell':
            plot_path = path.join(args.output_dir,
                                  'tput_across_cellular_links.pdf')
    elif args.type == 'delay':
        ax.set_ylabel('delay / lowest delay', fontsize=12)

        if args.link_type == 'eth':
            plot_path = path.join(args.output_dir, 'delay_across_links.pdf')
        elif args.link_type == 'cell':
            plot_path = path.join(args.output_dir,
                                  'delay_across_cellular_links.pdf')

    ax.grid()
    ax.set_xticks(x_data)
    ax.set_xticklabels(sorted(x_tick_labels), rotation=20)

    fig_w, fig_h = fig.get_size_inches()
    fig.set_size_inches(len(x_data), fig_h)

    lgd = ax.legend(bbox_to_anchor=(1, 0.5), loc='center left', fontsize=12)
    fig.savefig(plot_path, dpi=300, bbox_extra_artists=(lgd,),
                bbox_inches='tight', pad_inches=0.2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', metavar='DIR', required=True,
                        help='directory containing all the JSON data')
    parser.add_argument('--output-dir', metavar='DIR', required=True)
    parser.add_argument('--type', required=True, choices=['tput', 'delay'])
    parser.add_argument('--link-type', required=True, choices=['eth', 'cell'])
    args = parser.parse_args()

    data, x_tick_labels = parse_data(args)
    plot(args, data, x_tick_labels)


if __name__ == '__main__':
    main()
