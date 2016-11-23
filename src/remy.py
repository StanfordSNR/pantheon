#!/usr/bin/env python

import os
import sys
import usage
from subprocess import check_call
from get_open_port import get_open_tcp_port


def main():
    usage.check_args(sys.argv, os.path.basename(__file__), 'receiver_first')
    option = sys.argv[1]
    src_dir = os.path.abspath(os.path.dirname(__file__))
    submodule_dir = os.path.abspath(
        os.path.join(src_dir, '../third_party/genericCC'))
    rat_file = os.path.join(src_dir, 'RemyCC-2014-100x.dna')

    # build dependencies
    if option == 'deps':
        print "makepp libboost-dev libprotobuf-dev protobuf-c-compiler protobuf-compiler libjemalloc-dev"

    # build commands
    if option == 'build':
        cmd = 'cd %s && makepp && cp %s %s' % (submodule_dir, rat_file, submodule_dir)
        check_call(cmd, shell=True)
        
    # commands to be run after building and before running
    if option == 'init':
        pass

    # who goes first
    if option == 'who_goes_first':
        print 'Receiver first'

    # friendly name
    if option == 'friendly_name':
        print 'Remy'

    # receiver
    if option == 'receiver':
        port = get_open_tcp_port()
        print 'Listening on port: %s' % port
        sys.stdout.flush()
        cmd = [os.path.join(submodule_dir, 'receiver'), port]
        check_call(cmd)

    # sender
    if option == 'sender':
        ip = sys.argv[2]
        port = sys.argv[3]
        sender_file = os.path.join(submodule_dir, 'sender')
        cmd = "export MIN_RTT=1000000 && %s serverip=%s serverport=%s if=%s offduration=1 onduration=1000000 traffic_params=deterministic,num_cycles=1" % (sender_file, ip, port, rat_file)
        print cmd
        check_call(cmd, shell=True)


if __name__ == '__main__':
    main()
