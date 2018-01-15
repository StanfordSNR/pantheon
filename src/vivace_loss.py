#!/usr/bin/env python

import os
from os import path
from subprocess import check_call
from src_helpers import parse_arguments, check_default_qdisc
import project_root


def main():
    args = parse_arguments('receiver_first')

    cc_repo = path.join(project_root.DIR, 'third_party', 'vivace')
    recv_dir = path.join(cc_repo, 'vivace-loss', 'receiver')
    send_dir = path.join(cc_repo, 'vivace-loss', 'sender')
    recv_src = path.join(recv_dir, 'appserver')
    send_src = path.join(send_dir, 'gradient_descent_pcc_client')

    if args.option == 'run_first':
        print 'receiver'

    if args.option == 'setup_after_reboot':
        check_default_qdisc('vivace_loss')

    if args.option == 'receiver':
        os.environ['LD_LIBRARY_PATH'] = path.join(recv_dir)
        cmd = [recv_src]  # fixed port 9000
        check_call(cmd)

    if args.option == 'sender':
        os.environ['LD_LIBRARY_PATH'] = path.join(send_dir)
        cmd = [send_src, args.ip, '9000']
        check_call(cmd)


if __name__ == '__main__':
    main()
