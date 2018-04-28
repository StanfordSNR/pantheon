#!/usr/bin/env python

'''Example file to add a new congestion control scheme.

Please use Python 2.7 and conform to PEP8. Also use snake_case as file name and
make this file executable.
'''

from os import path
from subprocess import check_call
from src_helpers import parse_arguments, check_default_qdisc
import project_root  # 'project_root.DIR' is the root directory of Pantheon


def main():
    # use 'parse_arguments()' to ensure a common test interface
    args = parse_arguments('receiver_first')  # or 'sender_first'

    # paths to the sender and receiver executables, etc.
    cc_repo = path.join(project_root.DIR, 'third_party', 'example_cc')
    setup_src = path.join(cc_repo, 'example_setup')
    send_src = path.join(cc_repo, 'example_sender')
    recv_src = path.join(cc_repo, 'example_receiver')

    # [optional] dependencies
    if args.option == 'deps':
        print 'example_dep_1 example_dep_2'

    # [required] order to run: 'receiver' or 'sender'
    if args.option == 'run_first':
        print 'receiver'

    # [optional] persistent setup
    if args.option == 'setup':
        # avoid running anything as root here
        check_call([setup_src])

    # [required] setup performed after every reboot: check qdisc at least
    if args.option == 'setup_after_reboot':
        # by default, check if 'pfifo_fast' is used as qdisc
        # otherwise, change the qdisc in `config.yml` (refer to BBR as example)
        check_default_qdisc('example_cc')

    # [required] run the first side on port 'args.port'
    if args.option == 'receiver':
        cmd = [recv_src, args.port]
        check_call(cmd)

    # [required] run the other side to connect to the first side on 'args.ip'
    if args.option == 'sender':
        cmd = [send_src, args.ip, args.port]
        check_call(cmd)


if __name__ == '__main__':
    main()
