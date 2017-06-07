#!/usr/bin/env python

import os
from os import path
from subprocess import check_call, PIPE, Popen
from src_helpers import curr_time_sec, parse_arguments
import project_root


def main():
    args = parse_arguments('receiver_first')

    cc_repo = path.join(project_root.DIR, 'third_party', 'libutp')
    src = path.join(cc_repo, 'ucat-static')

    if args.option == 'run_first':
        print 'receiver'

    if args.option == 'setup':
        check_call(['make', '-j2'], cwd=cc_repo)

    if args.option == 'receiver':
        cmd = [src, '-l', '-p', args.port]
        # suppress stdout as it prints all the bytes received
        with open(os.devnull, 'w') as devnull:
            check_call(cmd, stdout=devnull)

    if args.option == 'sender':
        cmd = [src, args.ip, args.port]
        proc = Popen(cmd, stdin=PIPE)

        # send at full speed
        timeout = curr_time_sec() + 75
        while True:
            proc.stdin.write(os.urandom(1024))
            proc.stdin.flush()
            if curr_time_sec() > timeout:
                break

        if proc:
            proc.kill()


if __name__ == '__main__':
    main()
