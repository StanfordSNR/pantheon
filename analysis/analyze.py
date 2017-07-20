#!/usr/bin/env python

from os import path
from parse_arguments import parse_arguments
import project_root
from helpers.helpers import check_call


def main():
    args = parse_arguments(path.basename(__file__))

    analysis_dir = path.join(project_root.DIR, 'analysis')
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
