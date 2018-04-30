#!/usr/bin/env python

from os import path

import arg_parser
import context
from helpers.subprocess_wrappers import check_call


def main():
    args = arg_parser.parse_analyze()

    analysis_dir = path.join(context.src_dir, 'analysis')
    plot = path.join(analysis_dir, 'plot.py')
    report = path.join(analysis_dir, 'report.py')

    plot_cmd = ['python', plot]
    report_cmd = ['python', report]

    for cmd in [plot_cmd, report_cmd]:
        if args.data_dir:
            cmd += ['--data-dir', args.data_dir]
        if args.schemes:
            cmd += ['--schemes', args.schemes]
        if args.include_acklink:
            cmd += ['--include-acklink']

    check_call(plot_cmd)
    check_call(report_cmd)


if __name__ == '__main__':
    main()
