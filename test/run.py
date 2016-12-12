#!/usr/bin/env python

import os
import sys
import json
import random
import pantheon_helpers
from os import path
from helpers.pantheon_help import check_call, check_output, parse_remote
from helpers.parse_arguments import parse_arguments


def get_git_info(args, root_dir):
    git_info_cmd = (
        'echo -n \'git branch: \'; git rev-parse --abbrev-ref @ | head -c -1; '
        'echo -n \' @ \'; git rev-parse @; git submodule foreach --quiet '
        '\'echo $path @ `git rev-parse HEAD`; '
        'git status -s --untracked-files=no --porcelain\'')

    local_git_info = check_output(git_info_cmd, shell=True, cwd=root_dir)

    if args.remote:
        rd = parse_remote(args.remote)
        cmd = rd['ssh_cmd'] + ['cd %s; %s' % (rd['root_dir'], git_info_cmd)]
        remote_git_info = check_output(cmd)
        assert local_git_info == remote_git_info, (
            'Repository differed between local and remote sides.\n'
            'local git info:\n%s\nremote git info:\n%s\n' %
            (local_git_info, remote_git_info))

    return local_git_info


def create_metadata_file(args, cc_schemes, git_info, metadata_fname):
    metadata = dict()
    metadata['cc_schemes'] = ' '.join(cc_schemes)
    metadata['runtime'] = args.runtime
    metadata['flows'] = args.flows
    metadata['interval'] = args.interval
    metadata['sender_side'] = args.sender_side
    metadata['run_times'] = args.run_times

    if args.local_info:
        metadata['local_information'] = args.local_info

    if args.remote_info:
        metadata['remote_information'] = args.remote_info

    if args.local_if:
        metadata['local_interface'] = args.local_if

    if args.remote_if:
        metadata['remote_interface'] = args.remote_if

    if args.local_addr:
        metadata['local_address'] = args.local_addr

    if args.remote:
        remote_addr = args.remote.split(':')[0].split('@')[1]
        metadata['remote_address'] = remote_addr
        if args.ntp_addr:
            metadata['ntp_addr'] = remote_addr

    if git_info:
        metadata['git_information'] = git_info

    with open(metadata_fname, 'w') as metadata_file:
        json.dump(metadata, metadata_file)


def main():
    # arguments and source files location setup
    args = parse_arguments(path.basename(__file__))

    test_dir = path.abspath(path.dirname(__file__))
    root_dir = path.abspath(path.join(test_dir, os.pardir))
    pre_setup_src = path.join(test_dir, 'pre_setup.py')
    setup_src = path.join(test_dir, 'setup.py')
    test_src = path.join(test_dir, 'test.py')
    metadata_fname = path.join(test_dir, 'pantheon_metadata.json')

    # test congestion control schemes
    pre_setup_cmd = ['python', pre_setup_src]
    setup_cmd = ['python', setup_src]
    test_cmd = ['python', test_src]

    if args.remote:
        pre_setup_cmd += ['-r', args.remote]
        setup_cmd += ['-r', args.remote]
        test_cmd += ['-r', args.remote]

    test_cmd += ['-t', str(args.runtime), '-f', str(args.flows)]

    if args.flows > 1:
        test_cmd += ['--interval', str(args.interval)]

    if args.remote:
        test_cmd += ['--tunnel-server', args.server_side]
        if args.local_addr:
            test_cmd += ['--local-addr', args.local_addr]
        if args.ntp_addr:
            test_cmd += ['--ntp-addr', args.ntp_addr]

        test_cmd += ['--sender-side', args.sender_side]

    if args.local_if:
        pre_setup_cmd += ['--local-interface', args.local_if]
        test_cmd += ['--local-interface', args.local_if]

    if args.remote_if:
        pre_setup_cmd += ['--remote-interface', args.remote_if]
        test_cmd += ['--remote-interface', args.remote_if]

    run_setup = True
    run_test = True
    if args.run_only == 'setup':
        run_test = False
    elif args.run_only == 'test':
        run_setup = False

    cc_schemes = ['default_tcp', 'vegas', 'koho_cc', 'ledbat', 'pcc', 'verus',
                  'scream', 'sprout', 'webrtc', 'quic', 'taova']

    if args.random_order:
        random.shuffle(cc_schemes)

    # setup and run each congestion control
    if run_setup:
        get_git_info(args, root_dir)  # use as check for version mismatch
        check_call(pre_setup_cmd)
        for cc in cc_schemes:
            cmd = setup_cmd + [cc]
            check_call(cmd)

    if run_test:
        git_info = get_git_info(args, root_dir)
        create_metadata_file(args, cc_schemes, git_info, metadata_fname)

        for run_id in xrange(1, 1 + args.run_times):
            i = 0
            for cc in cc_schemes:
                i += 1
                sys.stderr.write('Running scheme %d of %d for experiment run '
                                 '%d of %d.' % (i, len(cc_schemes), run_id,
                                               args.run_times))
                cmd = test_cmd + ['--run-id', str(run_id), cc]
                check_call(cmd)


if __name__ == '__main__':
    main()
