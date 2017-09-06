#!/usr/bin/env python

from os import path
from subprocess import check_call
from src_helpers import parse_arguments, check_default_qdisc
import project_root


def main():
    args = parse_arguments('sender_first', 'poisson')

    cc_dir = path.join(project_root.DIR, 'src', 'poisson')
    send_src = path.join(cc_dir, 'sender.py')
    recv_src = path.join(cc_dir, 'receiver.py')

    if args.option == 'run_first':
        print 'sender'

    if args.option == 'setup_after_reboot':
        check_default_qdisc('poisson')

    if args.option == 'sender':
        cmd = [send_src, args.port, '--rate', args.rate]
        check_call(cmd)

    if args.option == 'receiver':
        cmd = [recv_src, args.ip, args.port]
        check_call(cmd)


if __name__ == '__main__':
    main()
