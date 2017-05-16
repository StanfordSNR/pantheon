#!/usr/bin/env python

import os
from os import path
from subprocess import call, check_call
import project_root
from helpers import parse_arguments, apply_patch


def main():
    args = parse_arguments('receiver_first')

    cc_repo = path.join(project_root.DIR, 'third_party', 'sprout')
    model = path.join(cc_repo, 'src', 'examples', 'sprout.model')
    src = path.join(cc_repo, 'src', 'examples', 'sproutbt2')

    # print build dependencies (separated by spaces)
    if args.option == 'deps':
        deps = ('libboost-math-dev libssl-dev libprotobuf-dev '
                'protobuf-compiler libncurses5-dev')
        print deps

    # print which side runs first (sender or receiver)
    if args.option == 'run_first':
        print 'receiver'

    # build the scheme
    if args.option == 'build':
        # apply patch to reduce MTU size
        apply_patch('sprout_mtu.patch', cc_repo)

        # make alone sufficient if autogen.sh and configure already run
        if call(['make', '-j2'], cwd=cc_repo) != 0:
            cmd = './autogen.sh && ./configure --enable-examples && make -j2'
            check_call(cmd, shell=True, cwd=cc_repo)

    # initialize the scheme before running
    if args.option == 'init':
        pass

    # run receiver
    if args.option == 'receiver':
        os.environ['SPROUT_MODEL_IN'] = model
        # Sprout prints 'listening on port' message to stdout
        check_call([src])

    # run sender
    if args.option == 'sender':
        os.environ['SPROUT_MODEL_IN'] = model
        cmd = [src, args.ip, args.port]
        check_call(cmd)


if __name__ == '__main__':
    main()
