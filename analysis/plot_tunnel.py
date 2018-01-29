#!/usr/bin/env python

from os import path
import argparse
import json
import numpy as np
import matplotlib_agg
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

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


def plot(args, real_data, emu_data):
    config = args['config']
    output_dir = args['dir']
    output_path = path.join(output_dir, args['name'] + '.svg')

    # plotting
    fig, ax = plt.subplots()

    for cc in emu_data:
        friendly_name = config[cc]['friendly_name']
        color = config[cc]['color']
        marker = config[cc]['marker']

        plot_point_cov(real_data[cc], nstd=1, ax=ax, color=color, alpha=0.5)

        x1, y1 = np.mean(real_data[cc], axis=0)
        ax.scatter(x1, y1, color=color, marker=marker)

        plot_point_cov(emu_data[cc], nstd=1, ax=ax, color='blue', alpha=0.5)

        x2, y2 = np.mean(emu_data[cc], axis=0)
        ax.scatter(x2, y2, marker=marker, facecolors='None',
                   edgecolors=color)
        ax.annotate(friendly_name, (x2, y2))

        #ax.plot([x1, x2], [y1, y2], color=color, linestyle='-')

    ax.set_xlim(40, 50)
    ax.set_ylim(80, 90)

    ax.invert_xaxis()
    ax.set_xlabel('95th percentile one-way delay (ms)', fontsize=12)
    ax.set_ylabel('Average throughput (Mbit/s)', fontsize=12)

    fig.savefig(output_path, bbox_inches='tight', pad_inches=0.2)

    plt.close('all')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--real')
    parser.add_argument('--emu')
    parser.add_argument('--schemes', metavar='"SCH1 SCH2..."')
    parser.add_argument('--dir', metavar='OUTPUT-DIR', default='.')
    parser.add_argument('--name', metavar='OUTPUT-NAME')
    args = vars(parser.parse_args())

    config = parse_config()['schemes']
    args['config'] = config

    with open(args['real']) as fh:
        real_data = json.load(fh)

    with open(args['emu']) as fh:
        emu_data = json.load(fh)

    real_data = parse_raw_data(real_data)
    emu_data = parse_raw_data(emu_data)
    plot(args, real_data, emu_data)


if __name__ == '__main__':
    main()
