#!/usr/bin/env python

import os
from os import path
from subprocess import check_call
from src_helpers import parse_arguments, apply_patch, check_default_qdisc
import project_root


def main():
    args = parse_arguments('receiver_first')

    cc_repo = path.join(project_root.DIR, 'third_party', 'pcc')
    recv_dir = path.join(cc_repo, 'receiver')
    send_dir = path.join(cc_repo, 'sender')
    recv_src = path.join(recv_dir, 'app', 'appserver')
    send_src = path.join(send_dir, 'app', 'appclient')

    if args.option == 'run_first':
        print 'receiver'

    if args.option == 'setup':
        # apply patch to reduce MTU size
        apply_patch('pcc.patch', cc_repo)

        check_call(['make'], cwd=recv_dir)
        check_call(['make'], cwd=send_dir)

    if args.option == 'setup_after_reboot':
        check_default_qdisc('pcc')

    if args.option == 'receiver':
        os.environ['LD_LIBRARY_PATH'] = path.join(recv_dir, 'src')
        cmd = [recv_src, args.port]
        check_call(cmd)

    if args.option == 'sender':
        os.environ['LD_LIBRARY_PATH'] = path.join(send_dir, 'src')
        cmd = [send_src, args.ip, args.port]
        # suppress debugging output to stderr
        with open(os.devnull, 'w') as devnull:
            check_call(cmd, stderr=devnull)


if __name__ == '__main__':
    main()
