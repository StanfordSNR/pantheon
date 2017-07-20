#!/usr/bin/env python

from os import path
from subprocess import check_call
from src_helpers import parse_arguments
import project_root


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

    if args.option == 'build':
        check_call(['makepp'], cwd=cc_repo)

    if args.option == 'receiver':
        cmd = [recv_src, args.port]
        check_call(cmd)

    if args.option == 'sender':
        rat_file = path.join(project_root.DIR, 'src', 'RemyCC-2014-100x.dna')
        sh_cmd = (
            'export MIN_RTT=1000000 && %s serverip=%s serverport=%s if=%s '
            'offduration=1 onduration=1000000 traffic_params=deterministic,'
            'num_cycles=1' % (send_src, args.ip, args.port, rat_file))
        check_call(sh_cmd, shell=True)


if __name__ == '__main__':
    main()
