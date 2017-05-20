#!/usr/bin/env python

import os
from os import path
from subprocess import check_call, PIPE, Popen
import project_root
from helpers import (
    curr_time_sec, get_open_port, print_port_for_tests, parse_arguments)


def main():
    args = parse_arguments('receiver_first')

    cc_repo = path.join(project_root.DIR, 'third_party', 'libutp')
    src = path.join(cc_repo, 'ucat-static')

    if args.option == 'run_first':
        print 'receiver'

    if args.option == 'setup':
        check_call(['make', '-j2'], cwd=cc_repo)

    if args.option == 'receiver':
        port = get_open_port()
        print_port_for_tests(port)

        cmd = [src, '-l', '-p', port]
        # suppress stdout as it prints all the bytes received
        with open(os.devnull, 'w') as devnull:
            check_call(cmd, stdout=devnull)

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

        if proc:
            proc.kill()


if __name__ == '__main__':
    main()
