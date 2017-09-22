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
from helpers.helpers import parse_config, order_legend_labels


def get_ranked_schemes(data):
    schemes_config = parse_config()['schemes']
    ranked_schemes = []
    ranked_friendly_names = []

    data_to_sort = []
    for cc in data:
        cc_name = schemes_config[cc]['friendly_name']

        score = np.log(data[cc]['tput_mean']) - np.log(data[cc]['delay_mean'])
        data_to_sort.append((cc, cc_name, score))

    data_to_sort = sorted(data_to_sort, key=lambda x: x[2], reverse=True)

    for i in xrange(len(data_to_sort)):
        print data_to_sort[i]
        ranked_schemes.append(data_to_sort[i][0])
        ranked_friendly_names.append(data_to_sort[i][1])

    return ranked_schemes, ranked_friendly_names


def parse_raw_data(raw_data):
    data = {}
    for cc in raw_data:
        data[cc] = {}
        tput_list = []
        delay_list = []

        for i in xrange(len(raw_data[cc])):
            tput_list.append(raw_data[cc][i][0])
            delay_list.append(raw_data[cc][i][1])

        data[cc]['tput_list'] = tput_list
        data[cc]['delay_list'] = delay_list
        data[cc]['tput_mean'] = np.mean(tput_list)
        data[cc]['delay_mean'] = np.mean(delay_list)

    return data


def plot(args, data, mean_plot, ranked_schemes, ranked_friendly_names):
    schemes_config = parse_config()['schemes']

    fig, ax = plt.subplots()

    for cc in reversed(ranked_schemes):
        if not data[cc]:
            sys.stderr.write('No performance data for scheme %s\n' % cc)
            continue

        cc_name = schemes_config[cc]['friendly_name']
        color = schemes_config[cc]['color']
        marker = schemes_config[cc]['marker']

        if mean_plot:
            x_data = data[cc]['delay_mean']
            y_data = data[cc]['tput_mean']
            ax.scatter(x_data, y_data, color=color, marker=marker)
            ax.annotate(cc_name, (x_data, y_data))
        else:
            x_data = data[cc]['delay_list']
            y_data = data[cc]['tput_list']
            ax.scatter(x_data, y_data, label=cc_name,
                       color=color, marker=marker)

    ax.set_xscale('log', basex=2)
    #ax.set_ylim(min, max)
    #ax.set_xlim(min, max)
    #ax.set_xticks([])
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
    ax.invert_xaxis()

    ax.set_xlabel('95th percentile one-way delay (ms)', fontsize=12)
    ax.set_ylabel('Average throughput (Mbit/s)', fontsize=12)
    ax.grid()

    if args.graph_name is None:
        base_name = path.basename(args.json).rsplit('.', 1)[0]
        if mean_plot:
            svg_name = base_name + '-mean.svg'
        else:
            svg_name = base_name + '.svg'

        real_graph = path.join(args.output_dir, svg_name)
    else:
        real_graph = path.join(args.output_dir, args.graph_name)

    if mean_plot:
        fig.savefig(real_graph, bbox_inches='tight', pad_inches=0.2)
    else:
        # order legends by Kleinrock score
        handles, labels = ax.get_legend_handles_labels()
        handles, labels = order_legend_labels(ranked_friendly_names,
                                              handles, labels)
        lgd = ax.legend(handles, labels, scatterpoints=1,
                        bbox_to_anchor=(1, 0.5),
                        loc='center left', fontsize=12)
        fig.savefig(real_graph, bbox_extra_artists=(lgd,),
                    bbox_inches='tight', pad_inches=0.2)

    sys.stderr.write('Saved plot as %s\n' % real_graph)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--json', metavar='FILENAME', required=True)
    parser.add_argument('--schemes', metavar='SCH1 SCH2...', required=True)
    parser.add_argument('--output-dir', metavar='DIR', default='.')
    parser.add_argument('--graph-name')
    args = parser.parse_args()

    with open(args.json) as json_file:
        raw_data = json.load(json_file)
        data = parse_raw_data(raw_data)

    ranked_schemes, ranked_friendly_names = get_ranked_schemes(data)
    plot(args, data, True, ranked_schemes, ranked_friendly_names)
    plot(args, data, False, ranked_schemes, ranked_friendly_names)


if __name__ == '__main__':
    main()
