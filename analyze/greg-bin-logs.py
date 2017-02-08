#!/usr/bin/env python

import sys
import argparse
import math
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

def write_out_bin(outfile, ms_per_bin, packet_bin, bin_bytes, num_lost):
    bin_megabits = bin_bytes * 8. / (1024. * 1024.)
    bin_mbps = (bin_megabits * 1000.) / ms_per_bin

    loss_rate = float(num_lost)/float(num_lost + len(packet_bin))
    outfile.write('%.3f %.3f\n' % (np.mean(packet_bin), bin_mbps))

def main():
    args = parse_arguments()

    prev_bin_idx = -1
    latest_bin = []
    latest_num_lost = 0
    latest_bin_bytes = 0
    with open(args.input_log_name) as input_log, open(args.output_log_name, 'w') as output_log:
        for line in input_log:
            (ts, prop_delay, size) = parse_line(line)

            bin_idx = int(ts / args.ms_per_bin)
            if bin_idx != prev_bin_idx:
                # write out bin
                if prev_bin_idx >= 0:
                    write_out_bin(output_log, args.ms_per_bin, latest_bin, latest_bin_bytes, latest_num_lost)
                    latest_bin = []
                    latest_num_lost = 0
                    latest_bin_bytes = 0
                if bin_idx - prev_bin_idx > 1:
                    print bin_idx - prev_bin_idx


            if math.isnan(prop_delay):
                latest_num_lost += 1
            else:
                latest_bin.append(prop_delay)
                latest_bin_bytes += size


            prev_bin_idx = bin_idx

        # can skip last bin


if __name__ == '__main__':
    main()
