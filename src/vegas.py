#!/usr/bin/env python

import os
import sys
import usage
from subprocess import check_call
from get_open_port import get_open_tcp_port


def main():
    usage.check_args(sys.argv, os.path.basename(__file__), 'receiver_first')
    option = sys.argv[1]
    src_dir = os.path.abspath(os.path.dirname(__file__))
    src_file = 'iperf'

    # build dependencies
    if option == 'deps':
        print 'iperf'

    # build
    if option == 'build':
        pass

    # commands to be run after building and before running
    if option == 'init':
        cmd = 'sudo modprobe tcp_vegas'
        check_call(cmd, shell=True)
        cmd = ('echo "vegas" | '
               'sudo tee /proc/sys/net/ipv4/tcp_allowed_congestion_control')
        check_call(cmd, shell=True)

    # who goes first
    if option == 'who_goes_first':
        print 'Receiver first'

    # friendly name
    if option == 'friendly_name':
        print 'TCP Vegas'

    # receiver
    if option == 'receiver':
        port = get_open_tcp_port()
        print 'Listening on port: %s' % port
        sys.stdout.flush()
        cmd = [src_file, '-Z', 'vegas', '-s', '-p', port]
        check_call(cmd)

    # sender
    if option == 'sender':
        ip = sys.argv[2]
        port = sys.argv[3]
        cmd = [src_file, '-Z', 'vegas', '-c', ip, '-p', port, '-t', '75']
        check_call(cmd)


if __name__ == '__main__':
    main()
