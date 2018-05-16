#!/usr/bin/env python

from os import path
from subprocess import check_call

import arg_parser
import context


def main():
    args = arg_parser.receiver_first()

    cc_repo = path.join(context.third_party_dir, 'scream-reproduce')
    recv_src = path.join(cc_repo, 'src', 'ScreamServer')
    send_src = path.join(cc_repo, 'src', 'ScreamClient')

    if args.option == 'setup':
        sh_cmd = './autogen.sh && ./configure && make -j'
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
