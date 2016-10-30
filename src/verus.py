#!/usr/bin/env python

import os
import sys
import usage
from subprocess import check_call, CalledProcessError
from get_open_port import get_open_udp_port


def main():
    usage.check_args(sys.argv, os.path.basename(__file__), usage.SEND_FIRST)
    option = sys.argv[1]
    src_dir = os.path.abspath(os.path.dirname(__file__))
    submodule_dir = os.path.abspath(
        os.path.join(src_dir, '../third_party/verus'))
    send_file = os.path.join(submodule_dir, 'src/verus_server')
    recv_file = os.path.join(submodule_dir, 'src/verus_client')

    # build dependencies
    if option == 'deps':
        deps_list = 'libtbb-dev libasio-dev libalglib-dev libboost-system-dev'
        print deps_list

    # build
    if option == 'build':
        # apply patch to reduce MTU size
        patch = os.path.join(src_dir, 'verus_mtu.patch')
        cmd = 'cd %s && git apply %s' % (submodule_dir, patch)
        try:
            check_call(cmd, shell=True)
        except CalledProcessError:
            sys.stderr.write('patch apply failed but assuming things okay '
                             '(patch applied previously?)\n')

        cmd = ('cd %s && ./bootstrap.sh && ./configure && make -j' %
               submodule_dir)
        check_call(cmd, shell=True)

    # commands to be run after building and before running
    if option == 'init':
        pass

    # who goes first
    if option == 'who_goes_first':
        print 'Sender first'

    # sender
    if option == 'sender':
        port = get_open_udp_port()
        print 'Listening on port: %s' % port
        sys.stdout.flush()
        cmd = [send_file, '-name', 'verus_tmp', '-p', port, '-t', '75']
        check_call(cmd)

    # receiver
    if option == 'receiver':
        ip = sys.argv[2]
        port = sys.argv[3]
        cmd = [recv_file, ip, '-p', port]
        check_call(cmd)


if __name__ == '__main__':
    main()
