#!/usr/bin/env python

import os
from os import path
from subprocess import check_call, Popen
from src_helpers import parse_arguments, apply_patch
import project_root


def main():
    args = parse_arguments('receiver_first')

    cc_repo = path.join(project_root.DIR, 'third_party', 'sprout')
    model = path.join(cc_repo, 'src', 'examples', 'sprout.model')
    src = path.join(cc_repo, 'src', 'examples', 'sproutbt2')

    if args.option == 'deps':
        print ('libboost-math-dev libssl-dev libprotobuf-dev '
               'protobuf-compiler libncurses5-dev')

    if args.option == 'run_first':
        print 'receiver'

    if args.option == 'setup':
        # apply patch to reduce MTU size
        apply_patch('sprout.patch', cc_repo)

        sh_cmd = './autogen.sh && ./configure --enable-examples && make -j2'
        check_call(sh_cmd, shell=True, cwd=cc_repo)

    if args.option == 'receiver':
        new_env = os.environ.copy()
        new_env['SPROUT_MODEL_IN'] = model

        cmd = [src, args.port]
        Popen(cmd, env=new_env).wait()

    if args.option == 'sender':
        new_env = os.environ.copy()
        new_env['SPROUT_MODEL_IN'] = model

        cmd = [src, args.ip, args.port]
        Popen(cmd, env=new_env).wait()


if __name__ == '__main__':
    main()
