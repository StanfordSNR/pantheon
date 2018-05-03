#!/usr/bin/env python

from os import path
from subprocess import check_call

import arg_parser
import context


def main():
    args = arg_parser.receiver_first()

    cc_repo = path.join(context.third_party_dir, 'genericCC')
    recv_src = path.join(cc_repo, 'receiver')
    send_src = path.join(cc_repo, 'sender')

    if args.option == 'deps':
        print ('makepp libboost-dev libprotobuf-dev protobuf-c-compiler '
               'protobuf-compiler libjemalloc-dev libboost-python-dev')
        return

    if args.option == 'setup':
        check_call(['makepp'], cwd=cc_repo)
        return

    if args.option == 'receiver':
        cmd = [recv_src, args.port]
        check_call(cmd)
        return

    if args.option == 'sender':
        rat_file = path.join(cc_repo, 'RemyCC-2014-100x.dna')
        sh_cmd = (
            'export MIN_RTT=1000000 && %s serverip=%s serverport=%s if=%s '
            'offduration=1 onduration=1000000 traffic_params=deterministic,'
            'num_cycles=1' % (send_src, args.ip, args.port, rat_file))
        check_call(sh_cmd, shell=True)
        return


if __name__ == '__main__':
    main()
