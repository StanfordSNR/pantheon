#!/usr/bin/env python

from os import path
import project_root
from helpers.helpers import (
    parse_arguments, check_call, check_output, update_submodules)


def install_deps(cc_src):
    cmd = ['python', cc_src, 'deps']
    deps = check_output(cmd).strip()

    if deps:
        cmd = 'sudo apt-get -y install ' + deps
        check_call(cmd, shell=True)


def setup(args):
    update_submodules()

    # enable IP forwarding
    cmd = 'sudo sysctl -w net.ipv4.ip_forward=1'
    check_call(cmd, shell=True)

    # setup specified schemes
    for cc in args.cc_schemes:
        cc_src = path.join(project_root.DIR, 'src', cc + '.py')

        if args.install_deps:
            # install dependencies
            install_deps(cc_src)

        if args.build:
            # build the scheme
            check_call(['python', cc_src, 'build'])

        check_call(['python', cc_src, 'init'])


def main():
    args = parse_arguments(path.abspath(__file__))
    setup(args)


if __name__ == '__main__':
    main()
