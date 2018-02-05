#!/usr/bin/env python

import json
import re
import sys
import argparse
import collections
from os import path

def interp_num(n):
    n = float(n)
    return int(n) if n.is_integer() else n


def collect_data(args):
    """ Given bandwidths, delays, schemes, parses all stats_run1.logs in
    the data directory and returns a dictionary as such:
        {scheme: {data}}

    data dictionary is as such:
        {bw: delay: {tput: X, delay: Y}}
    """

    # process args
    cc_schemes = args.schemes.split()
    if args.checkpoints is not None:
        checkpoints = args.checkpoints.split()
        for i in xrange(len(cc_schemes)):
            if checkpoints[i] != '-1':
                cc_schemes[i] += '-cp%s' % checkpoints[i]

    data_dir = args.data_dir
    bandwidths = sorted(map(interp_num, args.bandwidths.split()))
    delays = sorted(map(int, args.delays.split()))

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

            for delay in delays:
                data[cc][bw][delay] = {}

                folder = '%smbps-%dms' % (bw, delay)
                fname = '%s_stats_run%s.log' % (cc, run_id)
                stats_log_path = path.join(data_dir, folder , fname)

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
                            data[cc][bw][delay]['tput'] = ret

                        ret = re_delay(stats_log.readline())
                        if ret:
                            ret = float(ret.group(1))
                            data[cc][bw][delay]['delay'] = ret

                        ret = re_loss(stats_log.readline())
                        if ret:
                            ret = float(ret.group(1))
                            data[cc][bw][delay]['loss'] = ret

                        break

                stats_log.close()
        print 'Parsed data of scheme %s' % cc
    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', metavar='DIR', required=True)
    parser.add_argument('--bandwidths', metavar='BW1 BW2 ...', required=True)
    parser.add_argument('--delays', metavar='D1 D2 ...', required=True)
    parser.add_argument('--schemes', metavar='SCH1 SCH2...', required=True)
    parser.add_argument('--checkpoints', metavar='CP1 CP2...')

    args = parser.parse_args()

    data_dicts = collect_data(args)   # returns dictionary of scheme data

    for scheme in data_dicts:
        data = data_dicts[scheme]

        ordered = {k: collections.OrderedDict(sorted(v.iteritems()))
                   for k, v in data.iteritems()}
        ordered = collections.OrderedDict(sorted(ordered.iteritems()))
        data_dicts[scheme] = ordered

        json_path = path.join(args.data_dir, '%s.json' % scheme)

        with open(json_path, 'w') as outfile:
            json.dump(ordered, outfile)

    json_path = path.join(args.data_dir, 'perf_data.json')
    with open(json_path, 'w') as outfile:
        json.dump(data_dicts, outfile)


if __name__ == '__main__':
    main()
