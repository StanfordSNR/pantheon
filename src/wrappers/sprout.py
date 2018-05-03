#!/usr/bin/env python

import os
from os import path
from subprocess import check_call

import arg_parser
import context
from helpers import utils


def main():
    args = arg_parser.receiver_first()

    cc_repo = path.join(context.third_party_dir, 'sprout')
    model = path.join(cc_repo, 'src', 'examples', 'sprout.model')
    src = path.join(cc_repo, 'src', 'examples', 'sproutbt2')

    if args.option == 'deps':
        print ('libboost-math-dev libssl-dev libprotobuf-dev '
               'protobuf-compiler libncurses5-dev')
        return

    if args.option == 'setup':
        # apply patch to reduce MTU size
        utils.apply_patch('sprout.patch', cc_repo)

        sh_cmd = './autogen.sh && ./configure --enable-examples && make -j'
        check_call(sh_cmd, shell=True, cwd=cc_repo)
        return

    if args.option == 'receiver':
        os.environ['SPROUT_MODEL_IN'] = model
        cmd = [src, args.port]
        check_call(cmd)
        return

    if args.option == 'sender':
        os.environ['SPROUT_MODEL_IN'] = model
        cmd = [src, args.ip, args.port]
        check_call(cmd)
        return


if __name__ == '__main__':
    main()
