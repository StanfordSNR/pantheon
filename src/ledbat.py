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
    src_file = os.path.abspath(os.path.join(src_dir,
                               '../third_party/libutp/ucat-static'))
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

        port = check_output([find_unused_port_file])
        sys.stderr.write("Listening on port: %s\n" % port)

        cmd = [src_file, '-l', '-p', port]
        check_call(cmd, stdout=DEVNULL, stderr=DEVNULL)

    # sender
    if option == 'sender':
        if len(sys.argv) != 4:
            print_usage()

        ip = sys.argv[2]
        port = sys.argv[3] 

        cmd = [src_file, ip, port]
        proc = Popen(cmd, stdin=PIPE)
        
        timeout = time.time() + 15
        while True:
            proc.stdin.write(os.urandom(1024 * 1024))
            if time.time() > timeout:
                break
        proc.stdin.close()
    
    DEVNULL.close()

if __name__ == '__main__':
    main()
