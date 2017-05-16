#!/usr/bin/env python

import sys
import os
from os import path
from subprocess import check_call
import project_root
from helpers import get_open_port, parse_arguments, apply_patch


def main():
    args = parse_arguments('receiver_first')

    cc_repo = path.join(project_root.DIR, 'third_party', 'pcc')
    recv_dir = path.join(cc_repo, 'receiver')
    send_dir = path.join(cc_repo, 'sender')
    recv_src = path.join(recv_dir, 'app', 'appserver')
    send_src = path.join(send_dir, 'app', 'appclient')

    # print build dependencies (separated by spaces)
    if args.option == 'deps':
        pass

    # print which side runs first (sender or receiver)
    if args.option == 'run_first':
        print 'receiver'

    # build the scheme
    if args.option == 'build':
        # apply patch to reduce MTU size
        apply_patch('pcc_mtu.patch', cc_repo)

        check_call(['make', '-j2'], cwd=recv_dir)
        check_call(['make', '-j2'], cwd=send_dir)

    # initialize the scheme before running
    if args.option == 'init':
        pass

    # run receiver
    if args.option == 'receiver':
        port = get_open_port()
        print 'Listening on port: %s' % port
        sys.stdout.flush()

        os.environ['LD_LIBRARY_PATH'] = path.join(recv_dir, 'src')
        cmd = [recv_src, port]
        check_call(cmd)

    # run sender
    if args.option == 'sender':
        os.environ['LD_LIBRARY_PATH'] = path.join(send_dir, 'src')
        cmd = [send_src, args.ip, args.port]
        # suppress debugging output to stderr
        with open(os.devnull, 'w') as devnull:
            check_call(cmd, stderr=devnull)


if __name__ == '__main__':
    main()
