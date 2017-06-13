#!/usr/bin/env python

from os import path
from subprocess import check_call
from src_helpers import parse_arguments


def main():
    args = parse_arguments('sender_first')

    send_src = path.expanduser('~/RLCC/a3c/run_sender.py')
    recv_src = path.expanduser('~/RLCC/env/run_receiver.py')

    if args.option == 'run_first':
        print 'sender'

    if args.option == 'sender':
        cmd = [send_src, args.port]
        check_call(cmd)

    if args.option == 'receiver':
        cmd = [recv_src, args.ip, args.port]
        check_call(cmd)


if __name__ == '__main__':
    main()
