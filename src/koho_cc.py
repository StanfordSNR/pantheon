#!/usr/bin/env python

import os
import sys
import usage
from subprocess import call, check_call, CalledProcessError
from get_open_port import get_open_udp_port


def main():
    usage.check_args(sys.argv, os.path.basename(__file__), usage.RECV_FIRST)
    option = sys.argv[1]
    src_dir = os.path.abspath(os.path.dirname(__file__))
    submodule_dir = os.path.abspath(
        os.path.join(src_dir, '../third_party/koho_cc'))
    send_file = os.path.join(submodule_dir, 'datagrump/sender')
    recv_file = os.path.join(submodule_dir, 'datagrump/receiver')

    # build dependencies
    if option == 'deps':
        pass

    # build
    if option == 'build':
        # apply patch to reduce MTU size
        patch = os.path.join(src_dir, 'koho_cc_mtu.patch')
        cmd = 'cd %s && git apply %s' % (submodule_dir, patch)
        try:
            check_call(cmd, shell=True)
        except CalledProcessError:
            sys.stderr.write('patch apply failed but assuming things okay '
                             '(patch applied previously?)\n')

        # make alone sufficient if autogen.sh and configure already run
        cmd = 'cd %s && make -j' % submodule_dir
        if call(cmd, shell=True) is not 0:
            cmd = ('cd %s && ./autogen.sh && ./configure && make -j' %
                   submodule_dir)
            check_call(cmd, shell=True)

    # commands to be run after building and before running
    if option == 'init':
        pass

    # who goes first
    if option == 'who_goes_first':
        print 'Receiver first'

    # receiver
    if option == 'receiver':
        port = get_open_udp_port()
        print 'Listening on port: %s' % port
        sys.stdout.flush()
        cmd = [recv_file, port]
        check_call(cmd)

    # sender
    if option == 'sender':
        ip = sys.argv[2]
        port = sys.argv[3]
        cmd = [send_file, ip, port]
        check_call(cmd)


if __name__ == '__main__':
    main()
