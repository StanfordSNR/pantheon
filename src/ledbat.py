#!/usr/bin/env python

import os
import sys
import time
import usage
from subprocess import check_call, PIPE, Popen
from get_open_port import get_open_udp_port


def main():
    usage.check_args(sys.argv, os.path.basename(__file__), 'receiver_first')
    option = sys.argv[1]
    src_dir = os.path.abspath(os.path.dirname(__file__))
    submodule_dir = os.path.abspath(
        os.path.join(src_dir, '../third_party/libutp'))
    src_file = os.path.join(submodule_dir, 'ucat-static')
    DEVNULL = open(os.devnull, 'w')

    # build dependencies
    if option == 'deps':
        pass

    # build commands
    if option == 'build':
        cmd = 'cd %s && make -j' % submodule_dir
        check_call(cmd, shell=True)

    # commands to be run after building and before running
    if option == 'init':
        pass

    # who goes first
    if option == 'who_goes_first':
        print 'Receiver first'

    # friendly name
    if option == 'friendly_name':
        print 'LEDBAT'

    # receiver
    if option == 'receiver':
        port = get_open_udp_port()
        print 'Listening on port: %s' % port
        sys.stdout.flush()
        cmd = [src_file, '-l', '-p', port]
        # suppress stdout as it prints all the bytes received
        check_call(cmd, stdout=DEVNULL)

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
