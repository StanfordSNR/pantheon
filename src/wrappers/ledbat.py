#!/usr/bin/env python

import os
from os import path
from subprocess import check_call, PIPE, Popen
import time

import arg_parser
import context


def main():
    args = arg_parser.receiver_first()

    cc_repo = path.join(context.third_party_dir, 'libutp')
    src = path.join(cc_repo, 'ucat-static')

    if args.option == 'setup':
        check_call(['make', '-j'], cwd=cc_repo)
        return

    if args.option == 'receiver':
        cmd = [src, '-l', '-p', args.port]
        # suppress stdout as it prints all the bytes received
        with open(os.devnull, 'w') as devnull:
            check_call(cmd, stdout=devnull)
        return

    if args.option == 'sender':
        cmd = [src, args.ip, args.port]
        proc = Popen(cmd, stdin=PIPE)

        # send at full speed
        timeout = time.time() + 75
        while True:
            proc.stdin.write(os.urandom(1024))
            proc.stdin.flush()
            if time.time() > timeout:
                break

        if proc:
            proc.kill()
        return


if __name__ == '__main__':
    main()
