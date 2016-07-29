#!/usr/bin/python

import os, sys, time
from subprocess import check_output, check_call, PIPE, Popen
import usage
from get_open_port import *

def main():
    usage.check_args(sys.argv, os.path.basename(__file__), usage.RECV_FIRST)
    option = sys.argv[1]
    src_dir = os.path.abspath(os.path.dirname(__file__))
    submodule_dir = os.path.abspath(os.path.join(src_dir,
                                    '../third_party/libutp'))
    src_file = os.path.join(submodule_dir, 'ucat-static')
    DEVNULL = open(os.devnull, 'wb')

    # build dependencies
    if option == 'deps':
        pass

    # build commands
    if option == 'build':
        cmd = 'cd %s && make -j' % submodule_dir
        check_call(cmd, shell=True)

    # commands to be run after building and before running
    if option == 'initialize':
        pass

    # who goes first
    if option == 'who_goes_first':
        print 'Receiver first'

    # receiver
    if option == 'receiver':
        port = get_open_udp_port()
        sys.stderr.write('Listening on port: %s\n' % port)
        cmd = [src_file, '-l', '-p', port]
        check_call(cmd, stdout=DEVNULL) # suppress stdout as it prints all the bytes received

    # sender
    if option == 'sender':
        ip = sys.argv[2]
        port = sys.argv[3]
        cmd = [src_file, ip, port]
        proc = Popen(cmd, stdin=PIPE)

        timeout = time.time() + 75
        while True:
            proc.stdin.write(os.urandom(1024 * 1024))
            if time.time() > timeout:
                break
        proc.stdin.close()

    DEVNULL.close()

if __name__ == '__main__':
    main()
