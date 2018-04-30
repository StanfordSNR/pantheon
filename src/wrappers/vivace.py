#!/usr/bin/env python

import os
from os import path
from subprocess import check_call

import arg_parser
import context


def main():
    args = arg_parser.receiver_first()

    cc_repo = path.join(context.third_party_dir, 'vivace')
    recv_dir = path.join(cc_repo, 'receiver')
    send_dir = path.join(cc_repo, 'sender')
    recv_src = path.join(recv_dir, 'appserver')
    send_src = path.join(send_dir, 'gradient_descent_pcc_client')

    if args.option == 'receiver':
        os.environ['LD_LIBRARY_PATH'] = path.join(recv_dir)
        cmd = [recv_src]  # TODO: remove the fixed port 9000
        check_call(cmd)
        return

    if args.option == 'sender':
        os.environ['LD_LIBRARY_PATH'] = path.join(send_dir)
        cmd = [send_src, args.ip, '9000', '1']
        check_call(cmd)
        return


if __name__ == '__main__':
    main()
