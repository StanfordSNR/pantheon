#!/usr/bin/env python

from os import path
from subprocess import check_call
import project_root
from helpers import parse_arguments, apply_patch, TMPDIR


def main():
    args = parse_arguments('sender_first')

    cc_repo = path.join(project_root.DIR, 'third_party', 'verus')
    send_src = path.join(cc_repo, 'src', 'verus_server')
    recv_src = path.join(cc_repo, 'src', 'verus_client')

    if args.option == 'deps':
        print 'libtbb-dev libasio-dev libalglib-dev libboost-system-dev'

    if args.option == 'run_first':
        print 'sender'

    if args.option == 'setup':
        # apply patch to reduce MTU size
        apply_patch('verus.patch', cc_repo)

        sh_cmd = './bootstrap.sh && ./configure && make -j2'
        check_call(sh_cmd, shell=True, cwd=cc_repo)

    if args.option == 'sender':
        cmd = [send_src, '-name', TMPDIR, '-p', args.port, '-t', '75']
        check_call(cmd)

    if args.option == 'receiver':
        cmd = [recv_src, args.ip, '-p', args.port]
        check_call(cmd, cwd=TMPDIR)


if __name__ == '__main__':
    main()
