#!/usr/bin/env python

import sys
import arg_parser

import context
from helpers import kernel_ctl
from helpers.subprocess_wrappers import check_call


def sysctl(metric, value):
    check_call("sudo sysctl -w %s='%s'" % (metric, value), shell=True)


def main():
    args = arg_parser.parse_setup_system()

    # enable IP forwarding
    if args.enable_ip_forward:
        kernel_ctl.enable_ip_forwarding()

    # disable reverse path filtering
    if args.interface is not None:
        kernel_ctl.disable_rp_filter(args.interface)

    # set default qdisc
    if args.qdisc is not None:
        kernel_ctl.set_qdisc(args.qdisc)

    if args.reset_rmem:
        # reset socket receive buffer sizes to Linux default ones
        sysctl('net.core.rmem_default', 212992)
        sysctl('net.core.rmem_max', 212992)
    elif args.set_rmem:
        # set socket receive buffer
        sysctl('net.core.rmem_default', 16777216)
        sysctl('net.core.rmem_max', 33554432)
    elif args.reset_all_mem:
        # reset socket buffer sizes to Linux default ones
        sysctl('net.core.rmem_default', 212992)
        sysctl('net.core.rmem_max', 212992)
        sysctl('net.core.wmem_default', 212992)
        sysctl('net.core.wmem_max', 212992)
        sysctl('net.ipv4.tcp_rmem', '4096 87380 6291456')
        sysctl('net.ipv4.tcp_wmem', '4096 16384 4194304')
    elif args.set_all_mem:
        # set socket buffer sizes
        sysctl('net.core.rmem_default', 16777216)
        sysctl('net.core.rmem_max', 536870912)
        sysctl('net.core.wmem_default', 16777216)
        sysctl('net.core.wmem_max', 536870912)
        sysctl('net.ipv4.tcp_rmem', '4096 16777216 536870912')
        sysctl('net.ipv4.tcp_wmem', '4096 16777216 536870912')


if __name__ == '__main__':
    main()
