#!/usr/bin/env python

import sys
from subprocess import Popen, call, check_call, check_output
from src_helpers import parse_arguments, wait_and_kill_iperf


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

    # use fair queue as the default packet scheduler
    sh_cmd = 'sysctl net.core.default_qdisc'
    default_qdisc = check_output(sh_cmd, shell=True)
    default_qdisc = default_qdisc.split('=')[-1].strip()

    if default_qdisc != 'fq':
        sys.exit('Your default packet scheduler is "%s" currently. Please run '
                 '"sudo sysctl -w net.core.default_qdisc=fq" to use fair '
                 'queue as the default one for BBR to work.' % default_qdisc)


def main():
    args = parse_arguments('receiver_first')

    if args.option == 'deps':
        print 'iperf'

    if args.option == 'run_first':
        print 'receiver'

    if args.option == 'setup_after_reboot':
        setup_bbr()

    if args.option == 'receiver':
        cmd = ['iperf', '-Z', 'bbr', '-s', '-p', args.port]
        wait_and_kill_iperf(Popen(cmd))

    if args.option == 'sender':
        cmd = ['iperf', '-Z', 'bbr', '-c', args.ip, '-p', args.port,
               '-t', '75']
        wait_and_kill_iperf(Popen(cmd))


if __name__ == '__main__':
    main()
