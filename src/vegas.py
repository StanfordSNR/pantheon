#!/usr/bin/env python

from subprocess import check_call, check_output
from helpers import get_open_port, print_port_for_tests, parse_arguments


def setup_vegas():
    # enable tcp_vegas kernel module
    sh_cmd = 'sudo modprobe tcp_vegas'
    check_call(sh_cmd, shell=True)

    # add vegas to kernel-allowed congestion control list
    sh_cmd = 'sysctl net.ipv4.tcp_allowed_congestion_control'
    allowed_cc = check_output(sh_cmd, shell=True)
    allowed_cc = allowed_cc.split('=')[-1].split()

    if 'vegas' not in allowed_cc:
        allowed_cc.append('vegas')

        sh_cmd = 'sudo sysctl -w net.ipv4.tcp_allowed_congestion_control="%s"'
        check_call(sh_cmd % ' '.join(allowed_cc), shell=True)


def main():
    args = parse_arguments('receiver_first')

    if args.option == 'deps':
        print 'iperf'

    if args.option == 'run_first':
        print 'receiver'

    if args.option == 'setup_after_reboot':
        setup_vegas()

    if args.option == 'receiver':
        port = get_open_port()
        print_port_for_tests(port)

        cmd = ['iperf', '-Z', 'vegas', '-s', '-p', port]
        check_call(cmd)

    if args.option == 'sender':
        cmd = ['iperf', '-Z', 'vegas', '-c', args.ip, '-p', args.port,
               '-t', '75']
        check_call(cmd)


if __name__ == '__main__':
    main()
