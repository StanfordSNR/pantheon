#!/usr/bin/python

import os, sys
from subprocess import check_call
import usage

def main():
    usage.check_args(sys.argv, os.path.basename(__file__), usage.RECV_FIRST)
    option = sys.argv[1]
    src_dir = os.path.abspath(os.path.dirname(__file__))
    submodule_dir = os.path.abspath(os.path.join(src_dir,
                                    '../third_party/sprout'))
    src_file = os.path.join(submodule_dir, 'src/examples/sproutbt2')

    # build dependencies
    if option == 'deps':
        deps_list = 'libboost-math-dev libssl-dev' \
                    'libprotobuf-dev protobuf-compiler libncurses5-dev'
        print deps_list

    # build
    if option == 'build':
        cmd = 'cd %s && ./autogen.sh && ./configure --enable-examples && ' \
              'make -j' % submodule_dir
        check_call(cmd, shell=True)

    # commands to be run after building and before running
    if option == 'initialize':
        pass

    # who goes first
    if option == 'who_goes_first':
        print 'Receiver first'

    # receiver
    if option == 'receiver':
        os.environ['SPROUT_MODEL_IN'] = '%s/src/examples/sprout.model' \
                                         % submodule_dir
        # sproutbt2 prints the 'listening on port' message to stdout
        cmd = [src_file]
        check_call(cmd)

    # sender
    if option == 'sender':
        os.environ['SPROUT_MODEL_IN'] = '%s/src/examples/sprout.model' \
                                         % submodule_dir
        ip = sys.argv[2]
        port = sys.argv[3]
        cmd = [src_file, ip, port]
        check_call(cmd)

if __name__ == '__main__':
    main()
