#!/usr/bin/env python

import os
from os import path
from subprocess import check_call

import arg_parser
import context
from helpers import utils


def main():
    args = arg_parser.receiver_first()

    cc_repo = path.join(context.third_party_dir, 'pcc')
    recv_dir = path.join(cc_repo, 'receiver')
    send_dir = path.join(cc_repo, 'sender')
    recv_src = path.join(recv_dir, 'app', 'appserver')
    send_src = path.join(send_dir, 'app', 'appclient')

    if args.option == 'setup':
        # apply patch to reduce MTU size
        utils.apply_patch('pcc.patch', cc_repo)

        check_call(['make'], cwd=recv_dir)
        check_call(['make'], cwd=send_dir)
        return

    if args.option == 'receiver':
        os.environ['LD_LIBRARY_PATH'] = path.join(recv_dir, 'src')
        cmd = [recv_src, args.port]
        check_call(cmd)
        return

    if args.option == 'sender':
        os.environ['LD_LIBRARY_PATH'] = path.join(send_dir, 'src')
        cmd = [send_src, args.ip, args.port]
        # suppress debugging output to stderr
        with open(os.devnull, 'w') as devnull:
            check_call(cmd, stderr=devnull)
        return


if __name__ == '__main__':
    main()
