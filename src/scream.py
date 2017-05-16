#!/usr/bin/env python

import sys
from os import path
from subprocess import call, check_call
import project_root
from helpers import get_open_port, parse_arguments


def main():
    args = parse_arguments('receiver_first')

    scream_dir = path.join(project_root.DIR, 'src', 'scream')
    recv_src = path.join(scream_dir, 'ScreamServer')
    send_src = path.join(scream_dir, 'ScreamClient')

    # print build dependencies (separated by spaces)
    if args.option == 'deps':
        print 'dh-autoreconf'

    # print which side runs first (sender or receiver)
    if args.option == 'run_first':
        print 'receiver'

    # build the scheme
    if args.option == 'build':
        sourdough_dir = path.join(project_root.DIR, 'third_party', 'sourdough')
        for build_dir in [sourdough_dir, scream_dir]:
            # make alone sufficient if autogen.sh and configure already run
            if call(['make', '-j2'], cwd=build_dir) != 0:
                cmd = './autogen.sh && ./configure && make -j2'
                check_call(cmd, shell=True, cwd=build_dir)

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
