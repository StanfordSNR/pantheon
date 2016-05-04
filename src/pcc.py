#!/usr/bin/python

import os, sys, time
from subprocess import check_output, check_call, PIPE, Popen 
import usage

def print_usage():
    usage.print_usage(os.path.basename(__file__))
    sys.exit(1)

def main():
    # find paths of this script, find_unused_port and scheme source to run
    src_dir = os.path.abspath(os.path.dirname(__file__)) 
    find_unused_port_file = os.path.join(src_dir, 'find_unused_port')

    pcc_dir = os.path.abspath(os.path.join(src_dir, '../third_party/pcc'))
    recv_file = os.path.join(pcc_dir, 'receiver/app/appserver')
    send_file = os.path.join(pcc_dir, 'sender/app/appclient')
    DEVNULL = open(os.devnull, 'wb')

    if len(sys.argv) < 2:
        print_usage()

    option = sys.argv[1]

    # setup
    if option == 'setup':
        if len(sys.argv) != 2: 
            print_usage()

        sys.stderr.write("Receiver first.\n")

    # receiver
    if option == 'receiver':
        if len(sys.argv) != 2: 
            print_usage()

        port = check_output([find_unused_port_file])
        sys.stderr.write("Listening on port: %s\n" % port)

        cmd = 'export LD_LIBRARY_PATH=%s && %s %s' % \
              (os.path.join(pcc_dir, 'receiver/src'), recv_file, port)
        check_call(cmd, stdout=DEVNULL, stderr=DEVNULL, shell=True)

    # sender
    if option == 'sender':
        if len(sys.argv) != 4:
            print_usage()

        ip = sys.argv[2]
        port = sys.argv[3] 

        cmd = 'export LD_LIBRARY_PATH=%s && %s %s %s' % \
              (os.path.join(pcc_dir, 'sender/src'), send_file, ip, port)
        check_call(cmd, stdout=DEVNULL, stderr=DEVNULL, shell=True)

    DEVNULL.close()
    
if __name__ == '__main__':
    main()
