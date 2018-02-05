#!/usr/bin/env python

from os import path
import argparse
import json
import numpy as np
from matplotlib import rcParams
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Arial']
import matplotlib_agg
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import project_root
from helpers.helpers import parse_config, order_legend_labels
from analyze_helpers import plot_point_cov, parse_plot_setting


def get_ranked_schemes(args, data):
    ranked_schemes = []
    schemes = args['schemes']

    data_to_sort = []
    for cc in data:
        if schemes is not None and cc not in schemes:
            continue

        cc_mean = np.mean(data[cc], axis=0)
        score = np.log(cc_mean[1]) - np.log(cc_mean[0])
        data_to_sort.append((cc, score))

    data_to_sort = sorted(data_to_sort, key=lambda x: x[1], reverse=True)

    for t in data_to_sort:
        ranked_schemes.append(t[0])

    return ranked_schemes


def parse_raw_data(raw_data):
    data = {}

    for cc in raw_data:
        data[cc] = []

        for run_id in raw_data[cc]:
            if run_id == 'mean':
                continue

            if raw_data[cc][run_id] is None:
                continue

            delay = raw_data[cc][run_id]['all']['delay']
            tput = raw_data[cc][run_id]['all']['tput']

            data[cc].append([delay, tput])

        data[cc] = np.array(data[cc])

    return data


def plot(args, data, ranked_schemes):
    config = args['config']
    output_dir = args['dir']
    output_path = path.join(output_dir, args['name'] + '.svg')

    # create ranked friendly names
    ranked_friendly = []
    for cc in ranked_schemes:
        ranked_friendly.append(config[cc]['friendly_name'])

    # plotting
    fig, ax = plt.subplots()

    for cc in reversed(ranked_schemes):
        friendly_name = config[cc]['friendly_name']
        color = config[cc]['color']
        marker = config[cc]['marker']

        if 'alpha' in args['setting']:
            alpha = args['setting']['alpha']
        else:
            alpha = 0.5

        plot_point_cov(data[cc], nstd=1, ax=ax, color=color, alpha=alpha)

        x, y = np.mean(data[cc], axis=0)

        if marker == '*':
            marker_size = 100
        else:
            marker_size = 60
        ax.scatter(x, y, color=color, marker=marker, s=marker_size)
        ax.annotate(friendly_name, (x, y), color=color, fontsize=16)

    if 'xmin' in args['setting']:
        ax.set_xlim(left=args['setting']['xmin'])

    if 'xmax' in args['setting']:
        ax.set_xlim(right=args['setting']['xmax'])

    if 'ymin' in args['setting']:
        ax.set_ylim(bottom=args['setting']['ymin'])

    if 'ymax' in args['setting']:
        ax.set_ylim(top=args['setting']['ymax'])

    if 'xscale' in args['setting'] and args['setting']['xscale'] == 'log':
        ax.set_xscale('log', basex=2)
        ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))

    ax.invert_xaxis()
    ax.tick_params(labelsize=14)
    ax.set_xlabel('95th percentile one-way delay (ms)', fontsize=16)
    ax.set_ylabel('Average throughput (Mbit/s)', fontsize=16)

    fig.savefig(output_path, bbox_inches='tight')
    plt.close('all')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('json', metavar='JSON')
    parser.add_argument('--schemes', metavar='"SCH1 SCH2..."')
    parser.add_argument('--dir', metavar='OUTPUT-DIR', default='.')
    parser.add_argument('--name', metavar='OUTPUT-NAME', required=True)
    args = vars(parser.parse_args())

    config = parse_config()['schemes']
    args['config'] = config
    args['setting'] = parse_plot_setting()[args['name']]
    args['schemes'] = args['schemes'].split()

    with open(args['json']) as fh:
        raw_data = json.load(fh)

    data = parse_raw_data(raw_data)
    ranked_schemes = get_ranked_schemes(args, data)
    plot(args, data, ranked_schemes)


if __name__ == '__main__':
    main()
