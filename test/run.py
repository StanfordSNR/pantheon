#!/usr/bin/env python

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
    runtime = str(args.runtime)

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
        if private_key:
            setup_cmd += ['-i', private_key]
            test_cmd += ['-i', private_key]
        setup_cmd += ['-r', remote]
        test_cmd += ['-r', remote]

    test_cmd += ['-f', flows, '-t', runtime, '--interval', str(args.interval)]

    test_cmd += ['--tunnel-server', args.server_side]
    if args.server_side == 'local':
        test_cmd += ['--local-addr', args.local_addr]

    test_cmd += ['--sender-side', args.sender_side]

    if args.server_if:
        test_cmd += ['--server-interface', args.server_if]

    if args.client_if:
        test_cmd += ['--client-interface', args.client_if]

    # setup and run each congestion control
    for cc in cc_schemes:
        if not args.test_only:
            cmd = setup_cmd + [cc]
            sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
            check_call(cmd)

        if not args.setup_only:
            cmd = test_cmd + [cc]
            sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
            check_call(cmd)

    if not args.setup_only:
        cmd = ['perl', summary_plot_src] + cc_schemes
        sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
        check_call(cmd)

        cmd = ['python', combine_report_src] + cc_schemes
        sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
        check_call(cmd)


if __name__ == '__main__':
    main()
