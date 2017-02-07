#!/usr/bin/env python

import sys
import argparse
import numpy as np


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument( 'input_log_name', help='log to bin')
    parser.add_argument( 'output_log_name', help='binned log to output')
    parser.add_argument( 'ms_per_bin', type=int)

    return parser.parse_args()


def parse_line(line):
    (ts, prop_delay, size) = line.split()
    return (float(ts), float(prop_delay), int(size))


def main():
    args = parse_arguments()

    prev_bin_idx = -1
    latest_bin = []
    latest_bin_bytes = 0
    with open(args.input_log_name) as input_log, open(args.output_log_name, 'w') as output_log:
        for line in input_log:
            (ts, prop_delay, size) = parse_line(line)

            bin_idx = int(ts / args.ms_per_bin)
            if bin_idx == prev_bin_idx:
                latest_bin.append(prop_delay)
                latest_bin_bytes += size
            else:
                if prev_bin_idx >= 0:
                    bin_megabits = latest_bin_bytes * 8. / (1024. * 1024.)
                    bin_mbps = bin_megabits * 1000. / args.ms_per_bin
                    output_log.write('%.3f %.3f\n' % (np.mean(latest_bin), bin_mbps))

                latest_bin = [prop_delay]
                latest_bin_bytes = size
                if bin_idx - prev_bin_idx > 1:
                    print bin_idx - prev_bin_idx

            prev_bin_idx = bin_idx
                

if __name__ == '__main__':
    main()
