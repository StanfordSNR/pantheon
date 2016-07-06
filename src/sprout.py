#!/usr/bin/python

import os, sys 
from subprocess import check_output, check_call, PIPE
import usage

def print_usage():
    usage.print_usage(os.path.basename(__file__))
    sys.exit(1)

def main():
    # find paths of this script, find_unused_port and scheme source to run
    src_dir = os.path.abspath(os.path.dirname(__file__)) 
    src_file = os.path.abspath(os.path.join(src_dir,
                               '../third_party/sprout/src/examples/sproutbt2'))
    DEVNULL = open(os.devnull, 'wb')

    if len(sys.argv) < 2:
        print_usage()

    option = sys.argv[1]

    # setup
    if option == 'setup':
        if len(sys.argv) != 2: 
            print_usage()

        sys.stderr.write("Receiver first\n")

    # receiver
    if option == 'receiver':
        if len(sys.argv) != 2: 
            print_usage()

        sys.stderr.write("Listening on port: %s\n" % 60001)

        cmd = [src_file]
        check_call(cmd)

    # sender
    if option == 'sender':
        if len(sys.argv) != 4:
            print_usage()

        ip = sys.argv[2]
        port = sys.argv[3] 

        cmd = [src_file, ip, port]
        check_call(cmd)

    DEVNULL.close()

if __name__ == '__main__':
    main()
