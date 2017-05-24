#!/usr/bin/env python

import sys
from os import path
from parse_arguments import parse_arguments
import project_root
from helpers.helpers import (
    call, check_call, check_output, update_submodules, parse_config)


def install_deps(cc_src):
    cmd = ['python', cc_src, 'deps']
    deps = check_output(cmd).strip()

    if deps:
        cmd = 'sudo apt-get -y install ' + deps
        if call(cmd, shell=True) != 0:
            sys.stderr.write('Some dependencies failed to install '
                             'but assuming things okay.\n')


def setup(args):
    if not args.install_deps:
        # update submodules
        update_submodules()

        # enable IP forwarding
        sh_cmd = 'sudo sysctl -w net.ipv4.ip_forward=1'
        check_call(sh_cmd, shell=True)

        if args.interface is not None:
            # disable reverse path filtering
            rpf = 'net.ipv4.conf.%s.rp_filter'

            sh_cmd = 'sudo sysctl -w %s=0' % (rpf % 'all')
            check_call(sh_cmd, shell=True)

            sh_cmd = 'sudo sysctl -w %s=0' % (rpf % args.interface)
            check_call(sh_cmd, shell=True)

    # setup specified schemes
    cc_schemes = None

    if args.all:
        cc_schemes = parse_config().keys()
    elif args.schemes is not None:
        cc_schemes = args.schemes.split()

    if cc_schemes is not None:
        for cc in cc_schemes:
            cc_src = path.join(project_root.DIR, 'src', cc + '.py')

            # install dependencies
            if args.install_deps:
                install_deps(cc_src)
            else:
                # persistent setup across reboots
                if args.setup:
                    check_call(['python', cc_src, 'setup'])

                # setup required every time after reboot
                if cc == 'bbr':
                    if call(['python', cc_src, 'setup_after_reboot']) != 0:
                        sys.stderr.write('Warning: "%s.py setup_after_reboot"'
                                         ' failed but continuing\n' % cc)
                else:
                    check_call(['python', cc_src, 'setup_after_reboot'])


def main():
    args = parse_arguments(path.basename(__file__))
    setup(args)


if __name__ == '__main__':
    main()
