#!/usr/bin/env python

import sys
import argparse
import math
import numpy as np


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument( 'input_log_name', help='log to bin')
    parser.add_argument( 'output_log_name', help='interpolated log to output')
    parser.add_argument( 'sample_frequency', type=int)

    return parser.parse_args()


def parse_line(line):
    (ts, prop_delay, size) = line.split()
    return (float(ts), float(prop_delay), int(size))


def get_throughput(ms_per_bin, bin_bytes):
    bin_megabits = bin_bytes * 8. / (1024. * 1024.)
    bin_mbps = (bin_megabits * 1000.) / ms_per_bin
    return bin_mbps 

def write_output(output_log, sample_frequency, last_delay, latest_sample_bytes):
    throughput = get_throughput(sample_frequency, latest_sample_bytes)
    output_log.write('%.3f %.3f\n' % (last_delay, throughput))

def main():
    args = parse_arguments()

    with open(args.input_log_name) as input_log, open(args.output_log_name, 'w') as output_log:
        latest_sample_bytes = 0
        next_sample_time = 0
        last_delay = float('NaN')
        while True:
            line = input_log.readline()

            if line is None or line == '':
                if ts == next_sample_time:
                    write_output(output_log, args.sample_frequency, last_delay, latest_sample_bytes)
                return

            (ts, prop_delay, size) = parse_line(line)

            while ts > next_sample_time:
                write_output(output_log, args.sample_frequency, last_delay, latest_sample_bytes)

                latest_sample_bytes = 0
                next_sample_time += args.sample_frequency

            if not math.isnan(prop_delay):
                latest_sample_bytes += size

            last_delay = prop_delay

if __name__ == '__main__':
    main()
