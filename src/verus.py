#!/usr/bin/python

import os, sys 
from subprocess import check_output, check_call 
import usage

def print_usage():
    usage.print_usage(os.path.basename(__file__), order=usage.SEND_FIRST)
    sys.exit(1)

def main():
    # find paths of this script, find_unused_port and scheme source to run
    src_dir = os.path.abspath(os.path.dirname(__file__)) 
    find_unused_port_file = os.path.join(src_dir, 'find_unused_port')

    verus_dir = os.path.abspath(os.path.join(src_dir, '../third_party/verus/src'))
    send_file = os.path.join(verus_dir, 'verus_server')
    recv_file = os.path.join(verus_dir, 'verus_client')

    if len(sys.argv) < 2:
        print_usage()

    option = sys.argv[1]

    # setup
    if option == 'setup':
        if len(sys.argv) != 2: 
            print_usage()

        sys.stderr.write("Sender first\n")

    # sender
    if option == 'sender':
        if len(sys.argv) != 2: 
            print_usage()

        port = check_output([find_unused_port_file])
        sys.stderr.write("Listening on port: %s\n" % port)

        cmd = [send_file, '-name', 'verus_tmp', '-p', port, '-t', '15']
        check_call(cmd)
        
    # receiver
    if option == 'receiver':
        if len(sys.argv) != 4:
            print_usage()

        ip = sys.argv[2]
        port = sys.argv[3] 

        cmd = [recv_file, ip, '-p', port]
        check_call(cmd)

if __name__ == '__main__':
    main()
