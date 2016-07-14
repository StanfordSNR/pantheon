#!/usr/bin/python

import os, sys
from subprocess import check_output, check_call
import usage

def main():
    usage.check_args(sys.argv, os.path.basename(__file__), usage.RECV_FIRST)
    option = sys.argv[1]
    src_dir = os.path.abspath(os.path.dirname(__file__))
    submodule_dir = os.path.abspath(os.path.join(src_dir,
                                    '../third_party/pcc'))
    find_unused_port_file = os.path.join(src_dir, 'find_unused_port')
    recv_file = os.path.join(submodule_dir, 'receiver/app/appserver')
    send_file = os.path.join(submodule_dir, 'sender/app/appclient')
    DEVNULL = open(os.devnull, 'wb')

    # build
    if option == 'build':
        cmd = 'cd %s/sender && make && cd %s/receiver && make' % \
              (submodule_dir, submodule_dir)
        check_call(cmd, shell=True)

    # setup
    if option == 'setup':
        sys.stderr.write('Receiver first\n')

    # receiver
    if option == 'receiver':
        port = check_output([find_unused_port_file])
        sys.stderr.write('Listening on port: %s\n' % port)
        os.environ['LD_LIBRARY_PATH'] = '%s/receiver/src' % submodule_dir
        cmd = [recv_file, port]
        check_call(cmd, stdout=DEVNULL, stderr=DEVNULL)

    # sender
    if option == 'sender':
        ip = sys.argv[2]
        port = sys.argv[3]
        os.environ['LD_LIBRARY_PATH'] = '%s/sender/src' % submodule_dir
        cmd = [send_file, ip, port]
        check_call(cmd, stdout=DEVNULL, stderr=DEVNULL)

    DEVNULL.close()

if __name__ == '__main__':
    main()
