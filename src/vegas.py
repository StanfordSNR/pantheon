#!/usr/bin/python

import os, sys
from subprocess import check_output, check_call
import usage
from get_open_port import *

def main():
    usage.check_args(sys.argv, os.path.basename(__file__), usage.RECV_FIRST)
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
    if option == 'initialize':
        cmd = ['sudo', 'modprobe', 'tcp_vegas']
        check_call(cmd)

    # who goes first
    if option == 'who_goes_first':
        print 'Receiver first'

    # receiver
    if option == 'receiver':
        port = get_open_tcp_port()
        sys.stderr.write('Listening on port: %s\n' % port)
        cmd = [src_file, '-s', '-p', port]
        check_call(cmd)

    # sender
    if option == 'sender':
        ip = sys.argv[2]
        port = sys.argv[3]
        cmd = ['sudo', src_file, '-c', ip, '-p', port, '-t', '75', '-Z', 'vegas']
        check_call(cmd)

if __name__ == '__main__':
    main()
