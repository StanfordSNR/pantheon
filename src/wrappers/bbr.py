#!/usr/bin/env python

from subprocess import check_call

import arg_parser
import context
from helpers import kernel_ctl


def setup_bbr():
    # load tcp_bbr kernel module (only available since Linux Kernel 4.9)
    kernel_ctl.load_kernel_module('tcp_bbr')

    # add bbr to kernel-allowed congestion control list
    kernel_ctl.enable_congestion_control('bbr')

    # check if qdisc is fq
    kernel_ctl.check_qdisc('fq')


def main():
    args = arg_parser.receiver_first()

    if args.option == 'deps':
        print 'iperf'
        return

    if args.option == 'setup_after_reboot':
        setup_bbr()
        return

    if args.option == 'receiver':
        cmd = ['iperf', '-Z', 'bbr', '-s', '-p', args.port]
        check_call(cmd)
        return

    if args.option == 'sender':
        cmd = ['iperf', '-Z', 'bbr', '-c', args.ip, '-p', args.port,
               '-t', '75']
        check_call(cmd)
        return


if __name__ == '__main__':
    main()
