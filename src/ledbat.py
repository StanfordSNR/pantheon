#!/usr/bin/env python

import sys
import os
from os import path
from subprocess import check_call, PIPE, Popen
import project_root
from helpers import curr_time_sec, get_open_port, parse_arguments


def main():
    args = parse_arguments('receiver_first')

    cc_repo = path.join(project_root.DIR, 'third_party', 'libutp')
    src = path.join(cc_repo, 'ucat-static')

    # print build dependencies (separated by spaces)
    if args.option == 'deps':
        pass

    # print which side runs first (sender or receiver)
    if args.option == 'run_first':
        print 'receiver'

    # build the scheme
    if args.option == 'build':
        check_call(['make', '-j2'], cwd=cc_repo)

    # initialize the scheme before running
    if args.option == 'init':
        pass

    # run receiver
    if args.option == 'receiver':
        port = get_open_port()
        print 'Listening on port: %s' % port
        sys.stdout.flush()

        cmd = [src, '-l', '-p', port]
        # suppress stdout as it prints all the bytes received
        with open(os.devnull, 'w') as devnull:
            check_call(cmd, stdout=devnull)

    # run sender
    if args.option == 'sender':
        cmd = [src, args.ip, args.port]
        proc = Popen(cmd, stdin=PIPE)

        # send at full speed
        timeout = curr_time_sec() + 5
        while True:
            proc.stdin.write(os.urandom(1024 * 1024))
            proc.stdin.flush()
            if curr_time_sec() > timeout:
                break

        proc.terminate()


if __name__ == '__main__':
    main()
