#!/usr/bin/python

import os, sys, time
from subprocess import check_output, check_call, PIPE, Popen 
import usage

def main():
    # find paths of this script, find_unused_port and scheme source to run
    src_dir = os.path.abspath(os.path.dirname(__file__)) 
    find_unused_port_file = os.path.join(src_dir, 'find_unused_port')
    src_file = os.path.abspath(os.path.join(src_dir,
                               '../third_party/libutp/ucat-static'))
    DEVNULL = open(os.devnull, 'wb')

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

        cmd = [src_file, '-l', '-p', port]
        check_call(cmd, stdout=DEVNULL, stderr=DEVNULL)

    # sender
    if option == 'sender':
        if len(sys.argv) != 4:
            usage.print_usage(usage.RECV_FIRST)
            sys.exit(1)

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
