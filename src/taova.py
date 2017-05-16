#!/usr/bin/env python

import sys
from os import path
from subprocess import check_call
import project_root
from helpers import get_open_port, parse_arguments


def main():
    args = parse_arguments('receiver_first')

    cc_repo = path.join(project_root.DIR, 'third_party', 'genericCC')
    recv_src = path.join(cc_repo, 'receiver')
    send_src = path.join(cc_repo, 'sender')

    # print build dependencies (separated by spaces)
    if args.option == 'deps':
        deps = ('makepp libboost-dev libprotobuf-dev protobuf-c-compiler '
                'protobuf-compiler libjemalloc-dev')
        print deps

    # print which side runs first (sender or receiver)
    if args.option == 'run_first':
        print 'receiver'

    # build the scheme
    if args.option == 'build':
        check_call(['makepp'], cwd=cc_repo)

    # initialize the scheme before running
    if args.option == 'init':
        pass

    # run receiver
    if args.option == 'receiver':
        port = get_open_port()
        print 'Listening on port: %s' % port
        sys.stdout.flush()

        cmd = [recv_src, port]
        check_call(cmd)

    # run sender
    if args.option == 'sender':
        rat_file = path.join(project_root.DIR, 'src', 'RemyCC-2014-100x.dna')
        cmd = ('export MIN_RTT=1000000 && %s serverip=%s serverport=%s if=%s '
               'offduration=1 onduration=1000000 traffic_params=deterministic,'
               'num_cycles=1' % (send_src, args.ip, args.port, rat_file))
        check_call(cmd, shell=True)


if __name__ == '__main__':
    main()
