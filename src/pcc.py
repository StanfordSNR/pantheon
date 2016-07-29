#!/usr/bin/python

import os, sys
from subprocess import check_output, check_call
import usage
from get_open_port import *

def main():
    usage.check_args(sys.argv, os.path.basename(__file__), usage.RECV_FIRST)
    option = sys.argv[1]
    src_dir = os.path.abspath(os.path.dirname(__file__))
    submodule_dir = os.path.abspath(os.path.join(src_dir,
                                    '../third_party/pcc'))
    recv_file = os.path.join(submodule_dir, 'receiver/app/appserver')
    send_file = os.path.join(submodule_dir, 'sender/app/appclient')

    # build dependencies
    if option == 'deps':
        pass

    # build
    if option == 'build':
        cmd = 'cd %s/sender && make && cd %s/receiver && make' % \
              (submodule_dir, submodule_dir)
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
        os.environ['LD_LIBRARY_PATH'] = '%s/receiver/src' % submodule_dir
        cmd = [recv_file, port]
        check_call(cmd)

    # sender
    if option == 'sender':
        ip = sys.argv[2]
        port = sys.argv[3]
        os.environ['LD_LIBRARY_PATH'] = '%s/sender/src' % submodule_dir
        cmd = [send_file, ip, port]
        check_call(cmd)

if __name__ == '__main__':
    main()
