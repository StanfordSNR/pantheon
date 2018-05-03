#!/usr/bin/env python

'''REMOVE ME: Example file to add a new congestion control scheme.

Use Python 2.7 and conform to PEP8.
Use snake_case as file name and make this file executable.
'''

from os import path
from subprocess import check_call

import arg_parser
import context


def main():
    # use 'arg_parser' to ensure a common test interface
    args = arg_parser.receiver_first()  # or 'arg_parser.sender_first()'

    # paths to the sender and receiver executables, etc.
    cc_repo = path.join(context.third_party_dir, 'example_cc_repo')
    send_src = path.join(cc_repo, 'example_sender')
    recv_src = path.join(cc_repo, 'example_receiver')

    # [optional] dependencies of Debian packages
    if args.option == 'deps':
        print 'example_dep_1 example_dep_2'
        return

    # [optional] persistent setup that only needs to be run once
    if args.option == 'setup':
        # avoid running as root here
        return

    # [optional] non-persistent setup that should be performed on every reboot
    if args.option == 'setup_after_reboot':
        # avoid running as root here
        return

    # [required] run the first side on port 'args.port'
    if args.option == 'receiver':
        cmd = [recv_src, args.port]
        check_call(cmd)
        return

    # [required] run the other side to connect to the first side on 'args.ip'
    if args.option == 'sender':
        cmd = [send_src, args.ip, args.port]
        check_call(cmd)
        return


if __name__ == '__main__':
    main()
