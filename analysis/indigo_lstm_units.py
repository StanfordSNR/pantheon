#!/usr/bin/env python

import sys
import argparse
import json
from os import path
import numpy as np

from matplotlib import rcParams
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Arial']

import matplotlib_agg
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


def parse_json(json_path):
    with open(json_path) as fh:
        json_dict = json.load(fh)

    data = {}

    for i in json_dict:
        perf = json_dict[i]['200']['80']

        l = i.split('-')

        units = int(l[2])
        if len(l) == 4:
            cp = l[3]
        else:
            cp = 'default'

        if units not in data:
            data[units] = {}

        if cp not in data[units]:
            data[units][cp] = {}
            data[units][cp]['tput'] = float(perf['tput'])
            data[units][cp]['delay'] = float(perf['delay'])
        else:
            sys.stderr.write('error: checkpoint already exists\n')

    return data


def plot(args, data):
    output_dir = args.dir
    output_path = path.join(output_dir, args.name + '.svg')

    x = [1, 2, 4, 8, 16, 32, 64, 128, 256]

    # configure checkpoints
    cp = {}
    for units in x:
        cp[units] = 'default'

    cp[1] = 'cp100'
    cp[4] = 'cp110'
    cp[8] = 'cp40'
    #cp[16] = 'cp80'
    cp[64] = 'cp110'
    cp[256] = 'cp120'

    # construct data on y axis
    scores = []
    for units in x:
        tput = data[units][cp[units]]['tput']
        delay = data[units][cp[units]]['delay']
        score = 1.0 * tput / delay
        scores.append(score)

    # plot
    fig, ax = plt.subplots()
    ax.plot(x, scores, color='mediumblue', marker='x')
    ax.set_xlabel('Number of hidden units in LSTM', fontsize=16)
    ax.set_ylabel('avg throughput (Mbps) / p95 delay (ms)', fontsize=16)
    ax.set_xscale('log', basex=2)
    ax.tick_params(labelsize=14)
    ax.set_xticks(x)
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))

    fig.savefig(output_path, bbox_inches='tight')
    plt.close('all')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('json')
    parser.add_argument('--dir', metavar='OUTPUT-DIR', default='.')
    parser.add_argument('--name', metavar='OUTPUT-NAME', required=True)
    args = parser.parse_args()

    data = parse_json(args.json)
    plot(args, data)


if __name__ == '__main__':
    main()
