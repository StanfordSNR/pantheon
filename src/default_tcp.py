#!/usr/bin/python

import os, sys
from subprocess import check_output, check_call
import usage

def main():
    usage.check_args(sys.argv, os.path.basename(__file__), usage.RECV_FIRST)
    option = sys.argv[1]
    src_dir = os.path.abspath(os.path.dirname(__file__))
    find_unused_port_file = os.path.join(src_dir, 'find_unused_port')
    src_file = 'iperf'
    DEVNULL = open(os.devnull, 'wb')

    # build
    if option == 'build':
        pass

    # setup
    if option == 'setup':
        sys.stderr.write('Receiver first\n')

    # receiver
    if option == 'receiver':
        port = check_output([find_unused_port_file])
        sys.stderr.write('Listening on port: %s\n' % port)
        cmd = [src_file, '-s', '-p', port]
        check_call(cmd, stdout=DEVNULL, stderr=DEVNULL)

    # sender
    if option == 'sender':
        ip = sys.argv[2]
        port = sys.argv[3]
        cmd = [src_file, '-c', ip, '-p', port, '-t', '75']
        check_call(cmd, stdout=DEVNULL, stderr=DEVNULL)

    DEVNULL.close()

if __name__ == '__main__':
    main()
