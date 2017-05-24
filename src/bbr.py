#!/usr/bin/env python

import sys
from subprocess import call, check_call, check_output
from helpers import get_open_port, print_port_for_tests, parse_arguments


def setup_bbr():
    # enable tcp_bbr kernel module (only available since Linux Kernel 4.9)
    sh_cmd = 'sudo modprobe tcp_bbr'
    if call(sh_cmd, shell=True) != 0:
        sys.exit('Error: BBR is only available since Linux Kernel 4.9')

    # add bbr to kernel-allowed congestion control list
    sh_cmd = 'sysctl net.ipv4.tcp_allowed_congestion_control'
    allowed_cc = check_output(sh_cmd, shell=True)
    allowed_cc = allowed_cc.split('=')[-1].split()

    if 'bbr' not in allowed_cc:
        allowed_cc.append('bbr')

        sh_cmd = 'sudo sysctl -w net.ipv4.tcp_allowed_congestion_control="%s"'
        check_call(sh_cmd % ' '.join(allowed_cc), shell=True)


def main():
    args = parse_arguments('receiver_first')

    if args.option == 'deps':
        print 'iperf'

    if args.option == 'run_first':
        print 'receiver'

    if args.option == 'setup_after_reboot':
        setup_bbr()

    if args.option == 'receiver':
        port = get_open_port()
        print_port_for_tests(port)

        cmd = ['iperf', '-Z', 'bbr', '-s', '-p', port]
        if call(cmd) != 0:
            sys.exit('Error: BBR is not enabled yet')

    if args.option == 'sender':
        cmd = ['iperf', '-Z', 'bbr', '-c', args.ip, '-p', args.port,
               '-t', '75']
        if call(cmd) != 0:
            sys.exit('Error: BBR is not enabled yet')


if __name__ == '__main__':
    main()
