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
    DEVNULL = open(os.devnull, 'wb')

    # build dependencies
    if option == 'deps':
        deps_list = 'libboost-math-dev libboost-math1.54.0 libprotobuf8 ' \
                    'libprotobuf-dev protobuf-compiler libncurses5-dev'
        sys.stderr.write(deps_list + '\n')

    # build
    if option == 'build':
        cmd = 'cd %s && ./autogen.sh && ./configure --enable-examples && ' \
              'make -j' % submodule_dir
        check_call(cmd, shell=True)

    # setup
    if option == 'setup':
        os.environ['SPROUT_MODEL_IN'] = '%s/src/examples/sprout.model' \
                                        % submodule_dir
        sys.stderr.write('Receiver first\n')

    # receiver
    if option == 'receiver':
        sys.stderr.write('Listening on port: %s\n' % 60001)
        cmd = [src_file]
        check_call(cmd, stdout=DEVNULL, stderr=DEVNULL)

    # sender
    if option == 'sender':
        ip = sys.argv[2]
        port = sys.argv[3]
        cmd = [src_file, ip, port]
        check_call(cmd, stdout=DEVNULL, stderr=DEVNULL)

    DEVNULL.close()

if __name__ == '__main__':
    main()
