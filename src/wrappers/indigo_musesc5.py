#!/usr/bin/env python

from os import path
from subprocess import check_call

import arg_parser
import context


def main():
    args = arg_parser.receiver_first()

    cc_repo = path.join(context.third_party_dir, 'muses')
    recv_src = path.join(cc_repo, 'dagger', 'receiver.py')
    send_src = path.join(cc_repo, 'dagger', 'sender.py')
    model_path = path.join(cc_repo, 'dagger', 'model',
                           'indigo-musesC5', 'model')

    if args.option == 'setup':
        check_call(['sudo pip install tensorflow'], shell=True)
        return

    if args.option == 'receiver':
        cmd = [recv_src, args.port]
        check_call(cmd)
        return

    if args.option == 'sender':
        cmd = [send_src, args.ip, args.port, model_path]
        check_call(cmd)
        return


if __name__ == '__main__':
    main()
