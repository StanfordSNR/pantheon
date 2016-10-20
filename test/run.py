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
    flows = str(args.flows) if args.flows else None
    runtime = str(args.runtime) if args.runtime else None

    test_dir = path.abspath(path.dirname(__file__))
    setup_src = path.join(test_dir, 'setup.py')
    test_src = path.join(test_dir, 'test.py')
    summary_plot_src = path.join(test_dir, 'summary-plot.pl')
    combine_report_src = path.join(test_dir, 'combine_reports.py')

    # test congestion control schemes
    cc_schemes = ['default_tcp', 'vegas', 'koho_cc', 'ledbat', 'pcc', 'verus',
                  'scream', 'sprout', 'webrtc', 'quic']

    setup_cmd = ['python', setup_src]
    test_cmd = ['python', test_src]

    if remote:
        setup_cmd += ['-r', remote]
        test_cmd += ['-r', remote]
        if private_key:
            setup_cmd += ['-i', private_key]
            test_cmd += ['-i', private_key]

    if flows:
        test_cmd += ['-f', flows]

    if runtime:
        test_cmd += ['-t', runtime]

    for cc in cc_schemes:
        cmd = setup_cmd + [cc]
        sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
        check_call(cmd)

        cmd = test_cmd + [cc]
        sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
        check_call(cmd)

    '''
    cmd = ['perl', summary_plot_src, 'pantheon_summary.pdf'] + cc_schemes
    sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
    check_call(cmd)

    cmd = ['python', combine_report_src] + cc_schemes
    sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
    check_call(cmd)
    '''


if __name__ == '__main__':
    main()
