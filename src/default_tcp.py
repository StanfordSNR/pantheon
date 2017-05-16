#!/usr/bin/env python

import sys
from subprocess import check_call
from helpers import get_open_port, parse_arguments


def main():
    args = parse_arguments('receiver_first')

    # print build dependencies (separated by spaces)
    if args.option == 'deps':
        print 'iperf'

    # print which side runs first (sender or receiver)
    if args.option == 'run_first':
        print 'receiver'

    # build the scheme
    if args.option == 'build':
        pass

    # initialize the scheme before running
    if args.option == 'init':
        pass

    # run receiver
    if args.option == 'receiver':
        port = get_open_port()
        print 'Listening on port: %s' % port
        sys.stdout.flush()

        cmd = ['iperf', '-s', '-p', port]
        check_call(cmd)

    # run sender
    if args.option == 'sender':
        cmd = ['iperf', '-c', args.ip, '-p', args.port, '-t', '75']
        check_call(cmd)


if __name__ == '__main__':
    main()
