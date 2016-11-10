#!/usr/bin/env python

import sys
import random
from parse_arguments import parse_arguments
from os import path
from pantheon_help import check_call


def create_metadata_file(args, metadata_fname):
    metadata_file = open(metadata_fname, 'w')
    metadata_file.write(
        'runtime=%(runtime)s\n'
        'flows=%(flows)s\n'
        'interval=%(interval)s\n'
        'sender_side=%(sender_side)s\n'
        'run_times=%(run_times)s\n' % vars(args))

    if args.local_info:
        metadata_file.write('local_information=%s\n' % args.local_info)

    if args.remote_info:
        metadata_file.write('remote_information=%s\n' % args.remote_info)

    if args.local_if:
        metadata_file.write('local_interface=%s\n' % args.local_if)

    if args.remote_if:
        metadata_file.write('remote_interface=%s\n' % args.remote_if)

    if args.local_addr:
        metadata_file.write('local_address=%s\n' % args.local_addr)

    if args.remote:
        remote_addr = args.remote.split(':')[0].split('@')[1]
        metadata_file.write('remote_address=%s\n' % remote_addr)

    metadata_file.close()


def main():
    # arguments and source files location setup
    args = parse_arguments(path.basename(__file__))

    test_dir = path.abspath(path.dirname(__file__))
    setup_src = path.join(test_dir, 'setup.py')
    test_src = path.join(test_dir, 'test.py')
    summary_plot_src = path.join(test_dir, 'summary_plot.py')
    combine_report_src = path.join(test_dir, 'combine_reports.py')
    metadata_fname = path.join(test_dir, 'pantheon_metadata')

    # test congestion control schemes
    setup_cmd = ['python', setup_src]
    test_cmd = ['python', test_src]

    if args.remote:
        setup_cmd += ['-r', args.remote]
        test_cmd += ['-r', args.remote]

    test_cmd += [
        '-t', str(args.runtime), '-f', str(args.flows),
        '--interval', str(args.interval), '--tunnel-server', args.server_side]

    if args.local_addr:
        test_cmd += ['--local-addr', args.local_addr]

    test_cmd += ['--sender-side', args.sender_side]

    if args.local_if:
        setup_cmd += ['--local-interface', args.local_if]
        test_cmd += ['--local-interface', args.local_if]

    if args.remote_if:
        setup_cmd += ['--remote-interface', args.remote_if]
        test_cmd += ['--remote-interface', args.remote_if]

    run_setup = True
    run_test = True
    if args.run_only == 'setup':
        run_test = False
    elif args.run_only == 'test':
        run_setup = False

    # create metadata file to be used by combine_reports.py
    create_metadata_file(args, metadata_fname)

    cc_schemes = ['default_tcp', 'vegas', 'koho_cc', 'ledbat', 'pcc', 'verus',
                  'scream', 'sprout', 'webrtc', 'quic']

    if args.random_order:
        random.shuffle(cc_schemes)

    # setup and run each congestion control
    if run_setup:
        for cc in cc_schemes:
            cmd = setup_cmd + [cc]
            check_call(cmd)

    if run_test:
        for run_id in xrange(1, 1 + args.run_times):
            for cc in cc_schemes:
                cmd = test_cmd + ['--run-id', str(run_id), cc]
                check_call(cmd)

        cmd = ['python', summary_plot_src, '--run-times',
               str(args.run_times)] + cc_schemes
        check_call(cmd)

        cmd = ['python', combine_report_src, '--metadata-file', metadata_fname,
               '--run-times', str(args.run_times)] + cc_schemes
        check_call(cmd)


if __name__ == '__main__':
    main()
