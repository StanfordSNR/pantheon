#!/usr/bin/env python

import argparse
from os import path
from subprocess import check_call


def parse_arguments():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='option')

    subparsers.add_parser(
        'deps', help='print a space-separated list of build dependencies')
    subparsers.add_parser(
        'run_first', help='print which side (sender or receiver) runs first')
    subparsers.add_parser(
        'setup', help='set up the scheme (required to be run at the first '
        'time; must make persistent changes across reboots)')
    subparsers.add_parser(
        'setup_after_reboot', help='set up the scheme (required to be run '
        'every time after reboot)')

    receiver_parser = subparsers.add_parser('receiver', help='run receiver')
    sender_parser = subparsers.add_parser('sender', help='run sender')

    sender_parser.add_argument('port', help='port to listen on')
    sender_parser.add_argument('--cwnd', help='cwnd to guess', required=True)

    receiver_parser.add_argument(
	'ip', metavar='IP', help='IP address of sender')
    receiver_parser.add_argument('port', help='port of sender')

    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()

    send_src = path.expanduser('~/RLCC/tests/test_sender.py')
    recv_src = path.expanduser('~/RLCC/env/run_receiver.py')

    if args.option == 'run_first':
        print 'sender'

    if args.option == 'sender':
        cmd = [send_src, args.port, '--cwnd', args.cwnd]
        check_call(cmd)

    if args.option == 'receiver':
        cmd = [recv_src, args.ip, args.port]
        check_call(cmd)


if __name__ == '__main__':
    main()
