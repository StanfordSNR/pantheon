#!/usr/bin/env python

import matplotlib
matplotlib.use('Agg')

import sys
from os import path
import re
import numpy as np
import argparse
import matplotlib.pyplot as plt


def collect_data(args):
    # process args
    cc_schemes = args.schemes.split()
    data_dir = args.data_dir
    suffix = args.suffix
    bandwidths = sorted(map(int, args.bandwidths.split()))

    # collect data from stats logs
    data = {}
    flow_id = 1  # single flow only
    run_id = 1  # single run only

    re_tput = lambda x: re.match(r'Average throughput: (.*?) Mbit/s', x)
    re_delay = lambda x: re.match(
        r'95th percentile per-packet one-way delay: (.*?) ms', x)
    re_loss = lambda x: re.match(r'Loss rate: (.*?)%', x)

    for cc in cc_schemes:
        data[cc] = {}

        for bw in bandwidths:
            data[cc][bw] = {}

            fname = '%s_stats_run%s.log' % (cc, run_id)
            stats_log_path = path.join(data_dir, '%d%s' % (bw, suffix), fname)

            if not path.isfile(stats_log_path):
                sys.exit('%s does not exist!' % stats_log_path)

            stats_log = open(stats_log_path)

            while True:
                line = stats_log.readline()
                if not line:
                    break

                if 'Flow %d' % flow_id in line:
                    ret = re_tput(stats_log.readline())
                    if ret:
                        ret = float(ret.group(1))
                        data[cc][bw]['tput'] = ret

                    ret = re_delay(stats_log.readline())
                    if ret:
                        ret = float(ret.group(1))
                        data[cc][bw]['delay'] = ret

                    ret = re_loss(stats_log.readline())
                    if ret:
                        ret = float(ret.group(1))
                        data[cc][bw]['loss'] = ret

                    break

            stats_log.close()

    return data


def plot(data, output_dir, delay_suffix):
    fig, ax = plt.subplots()
    colors = ['b', 'g', 'r', 'y', 'c', 'm']
    color_i = 0

    for cc in data:
        x_data = []
        y_data = []

        sorted_bw_list = sorted(data[cc].keys())
        for bw in sorted_bw_list:
            x_data.append(bw)

            normalized_tput = 100.0 * data[cc][bw]['tput'] / bw
            delay = data[cc][bw]['delay']

            y_data.append(np.log(normalized_tput) - np.log(delay))

        color = colors[color_i]
        ax.plot(x_data, y_data, label=cc, color=color)

        color_i += 1
        if color_i == len(colors):
            color_i = 0

    # plot omniscient
    x_data = sorted(data['rlcc'].keys())
    y_data = [np.log(100.0) - np.log(float(delay_suffix)) for _ in x_data]
    ax.plot(x_data, y_data, label='omniscient', color='k')

    ax.set_xlabel('Link speed (Mbps)', fontsize=12)
    ax.set_ylabel('log(normalized throughput) - log(delay)', fontsize=12)

    ax.grid()
    ax.set_xticks(x_data)

    plot_path = path.join(output_dir, 'linkspeed_score_%s_delay.png' %
                         (delay_suffix))
    lgd = ax.legend(bbox_to_anchor=(1, 0.5), loc='center left', fontsize=12)
    fig.savefig(plot_path, dpi=300, bbox_extra_artists=(lgd,),
                bbox_inches='tight', pad_inches=0.2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', metavar='DIR')
    parser.add_argument('--bandwidths', metavar='BW1 BW2 ...')
    parser.add_argument('--delay', metavar='DELAY')
    parser.add_argument('--suffix')
    parser.add_argument('--schemes', metavar='SCHEME1 SCHEME2...')

    args = parser.parse_args()

    data = collect_data(args)
    plot(data, args.data_dir, args.delay)


if __name__ == '__main__':
    main()
