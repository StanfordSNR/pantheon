#!/usr/bin/env python

import sys
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
from helpers.helpers import parse_config
from analyze_helpers import plot_point_cov, parse_plot_setting


def get_abs_diff(metric_1, metric_2):
    return 1.0 * abs(metric_2 - metric_1) / metric_1


def compare(args, real_data, emu_data):
    flow = args['flow']

    tput_loss = 0.0
    delay_loss = 0.0
    cnt = 0

    for cc in args['schemes']:
        if cc not in real_data:
            sys.exit('%s not in real_data' % cc)
        if cc not in emu_data:
            sys.exit('%s not in emu_data' % cc)

        for flow_id in emu_data[cc]['mean']:
            if flow is not None:
                if flow_id != flow:
                    continue
            else:
                if flow_id == 'all':
                    continue

            emu_tput = emu_data[cc]['mean'][flow_id]['tput']
            emu_delay = emu_data[cc]['mean'][flow_id]['delay']

            if flow_id not in real_data[cc]['mean']:
                sys.exit('%s not in real_data[cc]["mean"]' % flow_id)

            real_tput = real_data[cc]['mean'][flow_id]['tput']
            real_delay = real_data[cc]['mean'][flow_id]['delay']

            tput_loss += get_abs_diff(real_tput, emu_tput)
            delay_loss += get_abs_diff(real_delay, emu_delay)
            cnt += 1

            print '%s_flow%s' % (cc, flow_id), 'tput', real_tput, emu_tput
            print '%s_flow%s' % (cc, flow_id), 'delay', real_delay, emu_delay

    tput_loss = tput_loss * 100.0 / cnt
    delay_loss = delay_loss * 100.0 / cnt
    overall_loss = (tput_loss + delay_loss) / 2.0

    print 'tput_loss', tput_loss
    print 'delay_loss', delay_loss
    print 'overall_loss', overall_loss


def parse_raw_data(args, raw_data):
    flow = args['flow']
    data = {}

    for cc in raw_data:
        data[cc] = []

        for run_id in raw_data[cc]:
            if run_id == 'median' or run_id == 'mean':
                continue

            if raw_data[cc][run_id] is None:
                continue

            if flow is None:
                delay = raw_data[cc][run_id]['all']['delay']
                tput = raw_data[cc][run_id]['all']['tput']
            else:
                delay = raw_data[cc][run_id][flow]['delay']
                tput = raw_data[cc][run_id][flow]['tput']

            data[cc].append([delay, tput])

        data[cc] = np.array(data[cc])

    return data


def plot(args, real_data, emu_data):
    config = args['config']
    output_dir = args['dir']
    output_path = path.join(output_dir, args['name'] + '.svg')

    # plotting
    fig, ax = plt.subplots()

    for cc in args['schemes']:
        friendly_name = config[cc]['friendly_name']
        color = config[cc]['color']
        marker = config[cc]['marker']

        plot_point_cov(real_data[cc], nstd=1, ax=ax, color=color, alpha=0.4)

        x1, y1 = np.mean(real_data[cc], axis=0)
        ax.scatter(x1, y1, color=color, marker=marker, s=60)

        x2, y2 = np.mean(emu_data[cc], axis=0)
        ax.scatter(x2, y2, marker=marker, facecolors='None',
                   edgecolors=color, s=60)
        ax.annotate(friendly_name, (x2, y2), color=color, fontsize=16)

        ax.plot([x1, x2], [y1, y2], color=color, linestyle='-')

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
    parser.add_argument('--real', help='folder containing perf_data.json')
    parser.add_argument('--emu', help='folder containing perf_data.json')
    parser.add_argument('--schemes', metavar='"SCH1 SCH2..."')
    parser.add_argument('--dir', metavar='OUTPUT-DIR', default='.')
    parser.add_argument('--name', metavar='OUTPUT-NAME', required=True)
    parser.add_argument('--flow', metavar='FLOW', help='None for all flows')
    args = vars(parser.parse_args())

    config = parse_config()['schemes']
    args['config'] = config
    args['setting'] = parse_plot_setting()[args['name']]
    args['schemes'] = args['schemes'].split()

    with open(path.join(args['real'], 'perf_data.json')) as fh:
        real_data = json.load(fh)

    with open(path.join(args['emu'], 'perf_data.json')) as fh:
        emu_data = json.load(fh)

    compare(args, real_data, emu_data)

    if args['name'] is not None:
        real_data = parse_raw_data(args, real_data)
        emu_data = parse_raw_data(args, emu_data)
        plot(args, real_data, emu_data)


if __name__ == '__main__':
    main()
