#!/usr/bin/python

import os, sys
from subprocess import check_output, check_call 
import usage

def print_usage():
    usage.print_usage(os.path.basename(__file__))
    sys.exit(1)

def main():
    src_dir = os.path.abspath(os.path.dirname(__file__))
    find_unused_port_file = os.path.join(src_dir, 'find_unused_port')
    src_file = 'iperf'

    if len(sys.argv) < 2:
        print_usage()

    option = sys.argv[1]

    # setup
    if option == 'setup':
        if len(sys.argv) != 2: 
            print_usage()
        
        cmd = 'sudo modprobe tcp_vegas && ' \
              'sudo bash -c "echo vegas > /proc/sys/net/ipv4/tcp_congestion_control"'
        print cmd
        check_call(cmd, shell=True)
        sys.stderr.write("Receiver first\n")

    # receiver
    if option == 'receiver':
        if len(sys.argv) != 2: 
            print_usage()

        port = check_output([find_unused_port_file])
        sys.stderr.write("Listening on port: %s\n" % port)

        cmd = [src_file, '-s', '-p', port, '-t', '75']
        check_call(cmd)

    # sender
    if option == 'sender':
        if len(sys.argv) != 4:
            print_usage()

        ip = sys.argv[2]
        port = sys.argv[3] 

        cmd = [src_file, '-c', ip, '-p', port, '-t', '75']
        check_call(cmd)

if __name__ == '__main__':
    main()
