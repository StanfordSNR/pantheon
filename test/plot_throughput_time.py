#!/usr/bin/env python

from os import path
from parse_arguments import parse_arguments


class PlotThroughputTime:
    def __init__(self, args):
        self.test_dir = path.abspath(path.dirname(__file__))
        self.src_dir = path.abspath(path.join(self.test_dir, '../src'))
        self.run_times = args.run_times
        self.cc_schemes = args.cc_schemes

    def plot_throughput_time(self):
        pass


def main():
    args = parse_arguments(path.basename(__file__))

    plot_throughput_time = PlotThroughputTime(args)
    plot_throughput_time.plot_throughput_time()


if __name__ == '__main__':
    main()
