#!/usr/bin/env python

from subprocess import Popen
from src_helpers import (parse_arguments, wait_and_kill_iperf,
                         check_default_qdisc)


def main():
    args = parse_arguments('receiver_first')

    if args.option == 'deps':
        print 'iperf'

    if args.option == 'run_first':
        print 'receiver'

    if args.option == 'setup_after_reboot':
        check_default_qdisc('default_tcp')

    if args.option == 'receiver':
        cmd = ['iperf', '-s', '-p', args.port]
        wait_and_kill_iperf(Popen(cmd))

    if args.option == 'sender':
        cmd = ['iperf', '-c', args.ip, '-p', args.port, '-t', '75']
        wait_and_kill_iperf(Popen(cmd))


if __name__ == '__main__':
    main()
