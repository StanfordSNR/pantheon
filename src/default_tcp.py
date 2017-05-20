#!/usr/bin/env python

from subprocess import check_call
from helpers import get_open_port, print_port_for_tests, parse_arguments


def main():
    args = parse_arguments('receiver_first')

    if args.option == 'deps':
        print 'iperf'

    if args.option == 'run_first':
        print 'receiver'

    if args.option == 'receiver':
        port = get_open_port()
        print_port_for_tests(port)

        cmd = ['iperf', '-s', '-p', port]
        check_call(cmd)

    if args.option == 'sender':
        cmd = ['iperf', '-c', args.ip, '-p', args.port, '-t', '75']
        check_call(cmd)


if __name__ == '__main__':
    main()
