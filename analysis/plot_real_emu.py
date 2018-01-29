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


def get_abs_diff(metric_1, metric_2):
    return 1.0 * abs(metric_2 - metric_1) / metric_1


def compare(real_data, emu_data):
    tput_loss = 0.0
    delay_loss = 0.0
    cnt = 0

    for cc in emu_data:
        if cc not in real_data:
            sys.exit('%s not in real_data' % cc)

        for flow_id in emu_data[cc]['mean']:
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

        x2, y2 = np.mean(emu_data[cc], axis=0)
        ax.scatter(x2, y2, marker=marker, facecolors='None',
                   edgecolors=color)
        ax.annotate(friendly_name, (x2, y2))

        ax.plot([x1, x2], [y1, y2], color=color, linestyle='-')

    #ax.set_xlim(,)
    #ax.set_ylim(,)

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

    with open(path.join(args['real'], 'perf_data.json')) as fh:
        real_data = json.load(fh)

    with open(path.join(args['emu'], 'perf_data.json')) as fh:
        emu_data = json.load(fh)

    compare(real_data, emu_data)

    if args['name'] is not None:
        real_data = parse_raw_data(real_data)
        emu_data = parse_raw_data(emu_data)
        plot(args, real_data, emu_data)


if __name__ == '__main__':
    main()
