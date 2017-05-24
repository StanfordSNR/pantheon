#!/usr/bin/env python

import sys
from os import path
from parse_arguments import parse_arguments
import project_root
from helpers.helpers import check_call


def main():
    args = parse_arguments(path.basename(__file__))

    if args.s3_link and args.s3_dst:
        # download .tar.xz from S3 and decompress

        tar_name = path.basename(args.s3_link)
        tar_path = path.join(args.s3_dst, tar_name)

        if path.exists(tar_path):
            sys.exit('%s already exists' % tar_path)

        check_call(['wget', args.s3_link, '-P', args.s3_dst])
        check_call(['tar', 'xf', tar_path, '-C', args.s3_dst])
        data_dir = path.join(args.s3_dst, tar_name.split('.', 1)[0])
    else:
        data_dir = args.data_dir

    data_dir = path.abspath(data_dir)

    analysis_dir = path.join(project_root.DIR, 'analysis')
    plot = path.join(analysis_dir, 'plot.py')
    report = path.join(analysis_dir, 'report.py')

    plot_cmd = ['python', plot]
    report_cmd = ['python', report]

    for cmd in [plot_cmd, report_cmd]:
        cmd += ['--data-dir', data_dir]
        if args.schemes:
            cmd += ['--schemes', args.schemes]
        if args.include_acklink:
            cmd += ['--include-acklink']

    check_call(plot_cmd)
    check_call(report_cmd)


if __name__ == '__main__':
    main()
