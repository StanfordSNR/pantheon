#!/usr/bin/env python

import os
from os import path
from subprocess import check_call
import project_root
from helpers import get_open_port, print_port_for_tests, parse_arguments


def main():
    args = parse_arguments('receiver_first')

    cc_repo = path.join(project_root.DIR, 'third_party', 'genericCC')
    recv_src = path.join(cc_repo, 'receiver')
    send_src = path.join(cc_repo, 'sender')

    if args.option == 'deps':
        print ('makepp libboost-dev libprotobuf-dev protobuf-c-compiler '
               'protobuf-compiler libjemalloc-dev')

    if args.option == 'run_first':
        print 'receiver'

    if args.option == 'setup':
        check_call(['makepp'], cwd=cc_repo)

    if args.option == 'receiver':
        port = get_open_port()
        print_port_for_tests(port)

        cmd = [recv_src, port]
        check_call(cmd)

    if args.option == 'sender':
        sh_cmd = (
            'export MIN_RTT=1000000 && %s serverip=%s serverport=%s '
            'offduration=1 onduration=1000000 traffic_params=deterministic,'
            'num_cycles=1 cctype=markovian delta_conf=constant_delta:1'
            % (send_src, args.ip, args.port))
        with open(os.devnull, 'w') as devnull:
            # suppress debugging output to stdout
            check_call(sh_cmd, shell=True, stdout=devnull)


if __name__ == '__main__':
    main()
