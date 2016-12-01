#!/usr/bin/env python

import os
import pantheon_helpers
from os import path
from helpers.parse_arguments import parse_arguments
from helpers.pantheon_help import check_call, check_output


def main():
    args = parse_arguments(path.basename(__file__))
    analyze_dir = path.abspath(path.dirname(__file__))

    if args.s3_link:
        # download .tar.xz from S3 and decompress
        os.chdir(args.s3_dir_prefix)
        tar_name = check_output(['basename', args.s3_link]).strip()
        tar_dir = tar_name[:-7]
        check_call(['rm', '-rf', tar_name, tar_dir])

        check_call(['wget', args.s3_link])
        check_call(['tar', 'xJf', tar_name])
        os.chdir(tar_dir)
    else:
        os.chdir(args.data_dir)

    # prepare scripts path
    analyze_pre_setup = path.join(analyze_dir, 'analysis_pre_setup.py')
    plot_summary = path.join(analyze_dir, 'plot_summary.py')
    plot_throughput_time = path.join(analyze_dir, 'plot_throughput_time.py')
    generate_report = path.join(analyze_dir, 'generate_report.py')

    if not args.no_pre_setup:
        check_call(['python', analysis_pre_setup])

    check_call(['python', plot_summary])
    check_call(['python', plot_throughput_time])
    check_call(['python', generate_report])


if __name__ == '__main__':
    main()
