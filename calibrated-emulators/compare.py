#!/usr/bin/env python

import math
import pickle
import argparse
import re
import numpy as np
from os import path


def get_abs_diff(metric_1, metric_2):
    if math.isnan(metric_1) or math.isnan(metric_2):
        return 10000.0
    else:
        return 1.0 * abs(metric_2 - metric_1) / metric_1


def parse_run_stats(stats):
    """ Takes in a list of stats split by line seen in pantheon_report.pdf,
    describing a run's statistics. Returns a dictionary in the form of
    {flow#: (tput, delay, rate)}

    Assumes the stats list is well-formed.
    For multiple flows, the sentinel flow # of 0 represents the total stats.
    """
    flow_stats = {}

    re_total = lambda x: re.match(r'-- Total of (.*?) flow', x)
    re_flow = lambda x: re.match(r'-- Flow (.*?):', x)
    re_tput = lambda x: re.match(r'Average throughput: (.*?) Mbit/s', x)
    re_delay = lambda x: re.match(
        r'95th percentile per-packet one-way delay: (.*?) ms', x)
    re_loss = lambda x: re.match(r'Loss rate: (.*?)%', x)

    flow_num = 0
    total_flows = 1
    idx = -1
    while idx < len(stats) - 1 and flow_num < total_flows:
        idx += 1
        line = stats[idx]

        flow_ret = re_total(line) or re_flow(line)
        if flow_ret is None or (re_total(line) is not None
                                and flow_ret.group(1) == '1'):
            continue

        if re_flow(line) is not None:
            flow_num = int(flow_ret.group(1))
        else:
            total_flows = int(flow_ret.group(1))

        if idx + 3 >= len(stats):
            break

        avg_tput_ret = re_tput(stats[idx + 1])
        if avg_tput_ret is None:
            continue

        owd_ret = re_delay(stats[idx + 2])
        if owd_ret is None:
            continue

        loss_ret = re_loss(stats[idx + 3])
        if loss_ret is None:
            continue

        flow_stats[flow_num] = (float(avg_tput_ret.group(1)),
                                float(owd_ret.group(1)),
                                float(loss_ret.group(1)))
    return flow_stats

def process_perf_data(perf_data_path):
    with open(perf_data_path) as perf_data_file:
        perf_data = pickle.load(perf_data_file)

    data = {}

    for scheme in perf_data:
        data[scheme] = {}
        data[scheme]['tput'] = []
        data[scheme]['delay'] = []
        for run_id in perf_data[scheme]:
            stats = perf_data[scheme][run_id]
            if stats is None:
                continue

            flows = parse_run_stats(stats.split('\n'))
            assert len(flows) == 1
            f = 1

            tput = flows[f][0]
            delay = flows[f][1]
            data[scheme]['tput'].append(float(tput))
            data[scheme]['delay'].append(float(delay))

    for scheme in data:
        tput_list = data[scheme]['tput']
        data[scheme]['tput'] = np.median(tput_list)

        delay_list = data[scheme]['delay']
        data[scheme]['delay'] = np.median(delay_list)

    return data


def compare(real_data, emu_data):
    tput_loss = 0.0
    delay_loss = 0.0
    cnt = 0
    for cc in emu_data:
        real_tput = real_data[cc]['tput']
        real_delay = real_data[cc]['delay']

        emu_tput = emu_data[cc]['tput']
        emu_delay = emu_data[cc]['delay']

        tput_loss += get_abs_diff(real_tput, emu_tput)
        delay_loss += get_abs_diff(real_delay, emu_delay)
        cnt += 1

        print cc, 'tput', real_tput, emu_tput
        print cc, 'delay', real_delay, emu_delay

    tput_loss = tput_loss * 100.0 / cnt
    delay_loss = delay_loss * 100.0 / cnt
    overall_loss = (tput_loss + delay_loss) / 2.0

    print 'tput_loss', tput_loss
    print 'delay_loss', delay_loss
    print 'overall_loss', overall_loss


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--real')
    parser.add_argument('--emu')
    args = parser.parse_args()

    real_perf_data = path.join(args.real, 'perf_data.pkl')
    real_data = process_perf_data(real_perf_data)

    emu_perf_data = path.join(args.emu, 'perf_data.pkl')
    emu_data = process_perf_data(emu_perf_data)

    compare(real_data, emu_data)


if __name__ == '__main__':
    main()
