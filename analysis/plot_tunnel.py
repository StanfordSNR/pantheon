#!/usr/bin/env python

from os import path
import argparse
import json
import numpy as np
from matplotlib import rcParams
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Times New Roman']
import matplotlib_agg
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy import stats

from analyze_helpers import plot_point_cov
import project_root
from helpers.helpers import parse_config


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


def plot(args, pcap_data, perf_data):
    config = args['config']
    output_dir = args['dir']
    output_path = path.join(output_dir, args['name'] + '.svg')

    # plotting
    fig, ax = plt.subplots()

    for cc in pcap_data:
        pcap_delay, pcap_tput = pcap_data[cc].T
        perf_delay, perf_tput = perf_data[cc].T

        pcap_color = 'blue'
        perf_color = 'orange'

        print 'KS (tput)', stats.ks_2samp(pcap_tput, perf_tput)
        print 'KS (delay)', stats.ks_2samp(pcap_delay, perf_delay)

        plot_point_cov(pcap_data[cc], nstd=1, ax=ax, color=pcap_color, alpha=0.4)
        ax.scatter(pcap_delay, pcap_tput, color=pcap_color, marker='o')

        x1, y1 = np.mean(pcap_data[cc], axis=0)
        ax.scatter(x1, y1, color=pcap_color, marker='*', s=100)
        ax.annotate('BBR (without tunnel)', (x1, y1), color=pcap_color, fontsize=14)

        plot_point_cov(perf_data[cc], nstd=1, ax=ax, color=perf_color, alpha=0.4)
        ax.scatter(perf_delay, perf_tput, color=perf_color, marker='d')

        x2, y2 = np.mean(perf_data[cc], axis=0)
        ax.scatter(x2, y2, color=perf_color, marker='*', s=100)
        ax.annotate('BBR (in tunnel)', (x2, y2), color=perf_color, fontsize=14)

        #ax.plot([x1, x2], [y1, y2], color='black', linestyle='-')

    #ax.set_xlim(45.5, 54.5)
    #ax.set_ylim(89.5, 101.5)
    #ax.set_ylim(68, 101.5)

    ax.invert_xaxis()
    ax.tick_params(labelsize=13)
    ax.set_xlabel('95th percentile one-way delay (ms)', fontsize=14)
    ax.set_ylabel('Average throughput (Mbit/s)', fontsize=14)

    fig.savefig(output_path, bbox_inches='tight', pad_inches=0.2)
    plt.close('all')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pcap', help='pcap_data.json')
    parser.add_argument('--perf', help='perf_data.json')
    parser.add_argument('--schemes', metavar='"SCH1 SCH2..."')
    parser.add_argument('--dir', metavar='OUTPUT-DIR', default='.')
    parser.add_argument('--name', metavar='OUTPUT-NAME')
    args = vars(parser.parse_args())

    config = parse_config()['schemes']
    args['config'] = config

    with open(args['pcap']) as fh:
        pcap_data = json.load(fh)

    with open(args['perf']) as fh:
        perf_data = json.load(fh)

    pcap_data = parse_raw_data(pcap_data)
    perf_data = parse_raw_data(perf_data)

    plot(args, pcap_data, perf_data)


if __name__ == '__main__':
    main()
