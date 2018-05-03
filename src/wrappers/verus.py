#!/usr/bin/env python

from os import path
from subprocess import check_call

import arg_parser
import context
from helpers import utils


def main():
    args = arg_parser.sender_first()

    cc_repo = path.join(context.third_party_dir, 'verus')
    send_src = path.join(cc_repo, 'src', 'verus_server')
    recv_src = path.join(cc_repo, 'src', 'verus_client')

    if args.option == 'deps':
        print 'libtbb-dev libasio-dev libalglib-dev libboost-system-dev'
        return

    if args.option == 'setup':
        # apply patch to reduce MTU size
        utils.apply_patch('verus.patch', cc_repo)

        sh_cmd = './bootstrap.sh && ./configure && make -j'
        check_call(sh_cmd, shell=True, cwd=cc_repo)
        return

    if args.option == 'sender':
        cmd = [send_src, '-name', utils.tmp_dir, '-p', args.port, '-t', '75']
        check_call(cmd, cwd=utils.tmp_dir)
        return

    if args.option == 'receiver':
        cmd = [recv_src, args.ip, '-p', args.port]
        check_call(cmd, cwd=utils.tmp_dir)
        return


if __name__ == '__main__':
    main()
