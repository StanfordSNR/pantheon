#!/usr/bin/env python

from os import path
from subprocess import check_call

import arg_parser
import context
from helpers import utils


def main():
    args = arg_parser.receiver_first()

    cc_repo = path.join(context.third_party_dir, 'calibrated_koho')
    recv_src = path.join(cc_repo, 'datagrump', 'receiver')
    send_src = path.join(cc_repo, 'datagrump', 'sender')

    if args.option == 'setup':
        # apply patch to reduce MTU size
        utils.apply_patch('calibrated_koho.patch', cc_repo)

        sh_cmd = './autogen.sh && ./configure && make -j2'
        check_call(sh_cmd, shell=True, cwd=cc_repo)
        return

    if args.option == 'receiver':
        cmd = [recv_src, args.port]
        check_call(cmd)
        return

    if args.option == 'sender':
        cmd = [send_src, args.ip, args.port]
        check_call(cmd)
        return


if __name__ == '__main__':
    main()
