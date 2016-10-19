#!/usr/bin/python

import sys
from parse_arguments import parse_arguments
from os import path
from subprocess import check_call


def main():
    # arguments and source files location setup
    args = parse_arguments(path.basename(__file__))
    remote = args.remote
    private_key = args.private_key
    flows = str(args.flows)

    test_dir = path.abspath(path.dirname(__file__))
    setup_src = path.join(test_dir, 'setup.py')
    test_src = path.join(test_dir, 'test.py')
    summary_plot_src = path.join(test_dir, 'summary-plot.pl')
    combine_report_src = path.join(test_dir, 'combine_reports.py')

    # test congestion control schemes
    cc_schemes = ['default_tcp', 'vegas', 'koho_cc', 'ledbat', 'pcc', 'verus',
                  'scream', 'sprout', 'webrtc', 'quic']

    for cc in cc_schemes:
        if remote:
            cmd = ['python', setup_src, '-r', remote, '-i', private_key, cc]
            sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
            check_call(cmd)

            cmd = ['python', test_src, '-r', remote, '-i', private_key,
                   '-f', flows, cc]
            sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
            check_call(cmd)
        else:
            cmd = ['python', setup_src, cc]
            sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
            check_call(cmd)

            cmd = ['python', test_src, '-f', flows, cc]
            sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
            check_call(cmd)

    cmd = ['perl', summary_plot_src, 'pantheon_summary.pdf'] + cc_schemes
    sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
    check_call(cmd)

    cmd = ['python', combine_report_src] + cc_schemes
    sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
    check_call(cmd)


if __name__ == '__main__':
    main()
