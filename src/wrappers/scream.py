#!/usr/bin/env python

from os import path
from subprocess import check_call

import arg_parser
import context


def main():
    args = arg_parser.receiver_first()

    scream_dir = path.join(context.src_dir, 'wrappers', 'scream')
    recv_src = path.join(scream_dir, 'ScreamServer')
    send_src = path.join(scream_dir, 'ScreamClient')

    if args.option == 'setup':
        sh_cmd = './autogen.sh && ./configure && make -j2'
        repo_dir = path.join(context.third_party_dir, 'sourdough')
        check_call(sh_cmd, shell=True, cwd=repo_dir)
        check_call(sh_cmd, shell=True, cwd=scream_dir)
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
