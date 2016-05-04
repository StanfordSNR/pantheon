#!/usr/bin/python

import os, sys
from subprocess import check_output, check_call 
import usage

def main():
    src_dir = os.path.abspath(os.path.dirname(__file__))
    find_unused_port_file = os.path.join(src_dir, 'find_unused_port')
    src_file = 'iperf'

    if len(sys.argv) < 2:
        usage.print_usage(usage.RECV_FIRST)
        sys.exit(1)

    option = sys.argv[1]

    # setup
    if option == 'setup':
        if len(sys.argv) != 2: 
            usage.print_usage(usage.RECV_FIRST)
            sys.exit(1)
        sys.stderr.write("Receiver first.\n")

    # receiver
    if option == 'receiver':
        if len(sys.argv) != 2: 
            usage.print_usage(usage.RECV_FIRST)
            sys.exit(1)

        port = check_output([find_unused_port_file])
        sys.stderr.write("Listening on port: %s\n" % port)

        cmd = [src_file, '-s', '-p', port, '-t', '15']
        check_call(cmd)

    # sender
    if option == 'sender':
        if len(sys.argv) != 4:
            usage.print_usage(usage.RECV_FIRST)
            sys.exit(1)

        ip = sys.argv[2]
        port = sys.argv[3] 

        cmd = [src_file, '-c', ip, '-p', port, '-t', '15']
        check_call(cmd)

if __name__ == '__main__':
    main()
