#!/usr/bin/env python

import os
import sys
import re
from os import path
from parse_arguments import parse_arguments
from subprocess import check_output


def find_throughput_delay(log_name):
    stats_log = open(log_name)
    throughput = None
    delay = None

    for line in stats_log:
        result = re.match(r'Average throughput: (.*?) Mbits/s', line)
        if result:
            throughput = result.group(1)

        result = re.match(r'95th percentile .* delay: (.*?) ms', line)
        if result:
            delay = result.group(1)

        if throughput and delay:
            break

    stats_log.close()
    return (throughput, delay)


def main():
    args = parse_arguments(path.basename(__file__))

    test_dir = path.abspath(path.dirname(__file__))
    src_dir = path.abspath(path.join(test_dir, '../src'))
    pantheon_summary_png = path.join(test_dir, 'pantheon_summary.png')

    pretty_names = {}
    data = {}
    for cc in args.cc_schemes:
        if cc not in pretty_names:
            cc_name = check_output(
                ['python', path.join(src_dir, cc + '.py'), 'friendly_name'])
            pretty_names[cc] = cc_name if cc_name else cc
            pretty_names[cc] = pretty_names[cc].strip().replace('_', '\\_')
            data[cc] = []

        for run_id in xrange(1, 1 + args.run_times):
            log_name = path.join(test_dir, '%s_stats_run%s.log' % (cc, run_id))
            data[cc].append(find_throughput_delay(log_name))


if __name__ == '__main__':
    main()
