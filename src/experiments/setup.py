#!/usr/bin/env python

from os import path
import sys

import arg_parser
import context
from helpers import utils
from helpers.subprocess_wrappers import call, check_call, check_output


def install_deps(cc_src):
    deps = check_output([cc_src, 'deps']).strip()

    if deps:
        if call('sudo apt-get -y install ' + deps, shell=True) != 0:
            sys.stderr.write('Some dependencies failed to install '
                             'but assuming things okay.\n')


def setup(args):
    # update submodules
    utils.update_submodules()

    # setup specified schemes
    cc_schemes = None

    if args.all:
        cc_schemes = utils.parse_config()['schemes'].keys()
    elif args.schemes is not None:
        cc_schemes = args.schemes.split()

    if cc_schemes is None:
        return

    for cc in cc_schemes:
        cc_src = path.join(context.src_dir, 'wrappers', cc + '.py')

        # install dependencies
        if args.install_deps:
            install_deps(cc_src)
        else:
            # persistent setup across reboots
            if args.setup:
                check_call([cc_src, 'setup'])

            # setup required every time after reboot
            if call([cc_src, 'setup_after_reboot']) != 0:
                sys.stderr.write('Warning: "%s.py setup_after_reboot"'
                                 ' failed but continuing\n' % cc)


def main():
    args = arg_parser.parse_setup()
    setup(args)


if __name__ == '__main__':
    main()
