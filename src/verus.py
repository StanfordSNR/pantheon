#!/usr/bin/env python

import sys
from os import path
from subprocess import call, check_call
import project_root
from helpers import get_open_port, parse_arguments, apply_patch, pantheon_tmp


def main():
    args = parse_arguments('sender_first')

    cc_repo = path.join(project_root.DIR, 'third_party', 'verus')
    send_src = path.join(cc_repo, 'src', 'verus_server')
    recv_src = path.join(cc_repo, 'src', 'verus_client')

    # print build dependencies (separated by spaces)
    if args.option == 'deps':
        deps = 'libtbb-dev libasio-dev libalglib-dev libboost-system-dev'
        print deps

    # print which side runs first (sender or receiver)
    if args.option == 'run_first':
        print 'sender'

    # build the scheme
    if args.option == 'build':
        # apply patch to reduce MTU size
        apply_patch('verus_mtu.patch', cc_repo)

        # make alone sufficient if bootstrap.sh and configure already run
        if call(['make', '-j2'], cwd=cc_repo) != 0:
            cmd = './bootstrap.sh && ./configure && make -j2'
            check_call(cmd, shell=True, cwd=cc_repo)

    # initialize the scheme before running
    if args.option == 'init':
        pass

    # run sender
    if args.option == 'sender':
        port = get_open_port()
        print 'Listening on port: %s' % port
        sys.stdout.flush()

        verus_tmp = path.join(pantheon_tmp(), 'verus_tmp')
        cmd = [send_src, '-name', verus_tmp, '-p', port, '-t', '75']
        check_call(cmd)

    # run receiver
    if args.option == 'receiver':
        verus_tmp = path.join(pantheon_tmp(), 'verus_tmp')
        cmd = [recv_src, args.ip, '-p', args.port]
        check_call(cmd, cwd=verus_tmp)


if __name__ == '__main__':
    main()
