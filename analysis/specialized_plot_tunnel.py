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


def plot(args):
    config = args['config']
    output_dir = args['dir']
    output_path = path.join(output_dir, args['name'] + '.svg')

    # plotting
    fig, ax = plt.subplots()

    for cc in args['schemes']:
        color = config[cc]['color']
        friendly = config[cc]['friendly_name']
        #marker = config[cc]['marker']
        marker = 'o'

        pcap_path = path.join(args['data_dir'], '{}_pcap_data.json'.format(cc))
        perf_path = path.join(args['data_dir'], '{}_perf_data.json'.format(cc))

        with open(pcap_path) as fh:
            pcap_data = json.load(fh)

        with open(perf_path) as fh:
            perf_data = json.load(fh)

        pcap_data = parse_raw_data(pcap_data)
        perf_data = parse_raw_data(perf_data)

        pcap_delay, pcap_tput = pcap_data[cc].T
        perf_delay, perf_tput = perf_data[cc].T

        print cc
        print 'KS (tput):', stats.ks_2samp(pcap_tput, perf_tput)
        print 'KS (delay):', stats.ks_2samp(pcap_delay, perf_delay)

        x1, y1 = np.mean(pcap_data[cc], axis=0)
        if cc != 'bbr':
            plot_point_cov(pcap_data[cc], nstd=1, ax=ax, color=color, alpha=0.5)
            #ax.scatter(pcap_delay, pcap_tput, color=color, marker='o', s=5)

            if cc == 'default_tcp':
                label = 'without tunnel'
            else:
                label = None
            ax.scatter(x1, y1, color=color, marker=marker, label=label)
            print 'without tunnel: mean tput (%.2f), 95th delay (%.2f)' % (y1, x1)
            #ax.annotate('{} (without tunnel)'.format(friendly),
            #            (x1, y1), color=color, fontsize=14)
        else:
            for t in pcap_tput:
                ax.axhline(t, xmin=0.98, xmax=1.0, color='black', linewidth=0.05)
            ax.axhline(y1, color=color, linewidth=1)
            print 'without tunnel: mean tput (%.2f)' % y1
            #ax.annotate('{} (in tunnel)'.format(friendly),
            #            (x1, y1), color=color, fontsize=14)

        plot_point_cov(perf_data[cc], nstd=1, ax=ax, alpha=0.5,
                       edgecolor=color, facecolor='none')
        #ax.scatter(perf_delay, perf_tput, marker='o', s=5,
        #           edgecolor=color, facecolor='none')

        x2, y2 = np.mean(perf_data[cc], axis=0)
        if cc == 'default_tcp':
            label = 'inside tunnel'
        else:
            label = None
        ax.scatter(x2, y2, marker=marker, facecolors='None', edgecolors=color,
                   label=label)
        print 'inside tunnel: mean tput (%.2f), 95th delay (%.2f)' % (y2, x2)

        if cc == 'bbr':
            ax.annotate('BBR inside tunnel', (x2, y2), color=color, fontsize=14)
        else:
            ax.annotate(friendly, (x2, y2), color=color, fontsize=14)
        #ax.annotate('{} (in tunnel)'.format(friendly),
        #            (x2, y2), color=color, fontsize=14)

        if cc != 'bbr':
            ax.plot([x1, x2], [y1, y2], color=color, linestyle='-')

    ax.annotate('Mean throughput of BBR without tunnel', (60, 90),
                color=config['bbr']['color'], fontsize=14)
    ax.annotate('Rug plot of BBR without tunnel', (20, 90),
                color=config['bbr']['color'], fontsize=14)

    ax.set_xlim(18, 72)
    ax.set_ylim(18, 105)
    #ax.set_ylim(68, 101.5)
    #ax.set_xscale('log', basex=2)
    #ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))

    ax.invert_xaxis()
    ax.tick_params(labelsize=13)
    ax.set_xlabel('95th percentile one-way delay (ms)', fontsize=14)
    ax.set_ylabel('Average throughput (Mbit/s)', fontsize=14)

    ax.legend(scatterpoints=1, loc='lower left', fontsize=14)

    fig.savefig(output_path, bbox_inches='tight', pad_inches=0.2)
    plt.close('all')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', metavar='DATA-DIR', required=True)
    parser.add_argument('--schemes', metavar='"SCH1 SCH2..."')
    parser.add_argument('--dir', metavar='OUTPUT-DIR', default='.')
    parser.add_argument('--name', metavar='OUTPUT-NAME')
    args = vars(parser.parse_args())

    config = parse_config()['schemes']
    args['config'] = config
    args['schemes'] = args['schemes'].split()

    plot(args)


if __name__ == '__main__':
    main()
