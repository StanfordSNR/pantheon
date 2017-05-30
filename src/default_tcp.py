#!/usr/bin/env python

from subprocess import check_call
from helpers import parse_arguments


def main():
    args = parse_arguments('receiver_first')

    if args.option == 'deps':
        print 'iperf'

    if args.option == 'run_first':
        print 'receiver'

    if args.option == 'receiver':
        cmd = ['iperf', '-s', '-p', args.port]
        check_call(cmd)

    if args.option == 'sender':
        cmd = ['iperf', '-c', args.ip, '-p', args.port, '-t', '75']
        check_call(cmd)


if __name__ == '__main__':
    main()
