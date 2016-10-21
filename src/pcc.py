#!/usr/bin/python

import os
import sys
import usage
from subprocess import check_call
from get_open_port import get_open_udp_port


def main():
    usage.check_args(sys.argv, os.path.basename(__file__), usage.RECV_FIRST)
    option = sys.argv[1]
    src_dir = os.path.abspath(os.path.dirname(__file__))
    submodule_dir = os.path.abspath(
        os.path.join(src_dir, '../third_party/pcc'))
    recv_dir = os.path.join(submodule_dir, 'receiver')
    send_dir = os.path.join(submodule_dir, 'sender')
    DEVNULL = open(os.devnull, 'w')

    # build dependencies
    if option == 'deps':
        pass

    # build
    if option == 'build':
        cmd = 'cd %s && make && cd %s && make' % (send_dir, recv_dir)
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
        print 'Listening on port: %s' % port
        sys.stdout.flush()
        os.environ['LD_LIBRARY_PATH'] = os.path.join(recv_dir, 'src')
        cmd = [os.path.join(recv_dir, 'app/appserver'), port]
        check_call(cmd)

    # sender
    if option == 'sender':
        ip = sys.argv[2]
        port = sys.argv[3]
        os.environ['LD_LIBRARY_PATH'] = os.path.join(send_dir, 'src')
        cmd = [os.path.join(send_dir, 'app/appclient'), ip, port]
        check_call(cmd, stderr=DEVNULL)


if __name__ == '__main__':
    main()
