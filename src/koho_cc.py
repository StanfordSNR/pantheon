#!/usr/bin/env python

import sys
from os import path
from subprocess import call, check_call
import project_root
from helpers import get_open_port, parse_arguments, apply_patch


def main():
    args = parse_arguments('receiver_first')

    cc_repo = path.join(project_root.DIR, 'third_party', 'koho_cc')
    recv_src = path.join(cc_repo, 'datagrump', 'receiver')
    send_src = path.join(cc_repo, 'datagrump', 'sender')

    # print build dependencies (separated by spaces)
    if args.option == 'deps':
        pass

    # print which side runs first (sender or receiver)
    if args.option == 'run_first':
        print 'receiver'

    # build the scheme
    if args.option == 'build':
        # apply patch to reduce MTU size
        apply_patch('koho_cc_mtu.patch', cc_repo)

        # make alone sufficient if autogen.sh and configure already run
        if call(['make', '-j2'], cwd=cc_repo) != 0:
            cmd = './autogen.sh && ./configure && make -j2'
            check_call(cmd, shell=True, cwd=cc_repo)

    # initialize the scheme before running
    if args.option == 'init':
        pass

    # run receiver
    if args.option == 'receiver':
        port = get_open_port()
        print 'Listening on port: %s' % port
        sys.stdout.flush()

        cmd = [recv_src, port]
        check_call(cmd)

    # run sender
    if args.option == 'sender':
        cmd = [send_src, args.ip, args.port]
        check_call(cmd)


if __name__ == '__main__':
    main()
