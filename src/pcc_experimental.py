#!/usr/bin/env python

'''Example file to add a new congestion control scheme.

Please use Python 2.7 and conform to PEP8. Also use snake_case as file name and
make this file executable.
'''

import os
from os import path
from subprocess import check_call
from src_helpers import parse_arguments, check_default_qdisc
import project_root  # 'project_root.DIR' is the root directory of Pantheon
#import sys # we'd like to pass sys.argv into PCC-Vivace, but we can't quite 
            # do that yet (parse_arguments doesn't allow arguments that are
            # unknown to this script).

def main():
    # use 'parse_arguments()' to ensure a common test interface
    args = parse_arguments('receiver_first')  # or 'sender_first'

    # paths to the sender and receiver executables, etc.
    cc_repo = path.join(project_root.DIR, 'third_party', 'pcc-experimental')
    src_dir = path.join(cc_repo, 'src')
    lib_dir = path.join(src_dir, 'core')
    app_dir = path.join(src_dir, 'app')
    send_src = path.join(app_dir, 'pccclient')
    recv_src = path.join(app_dir, 'pccserver')

    if args.option == 'run_first':
        print 'receiver'

    if args.option == 'setup':
        check_call(['make'], cwd=src_dir)

    if args.option == 'setup_after_reboot':
        # by default, check if 'pfifo_fast' is used as qdisc
        # otherwise, change the qdisc in `config.yml` (refer to BBR as example)
        check_default_qdisc('pcc_experimental')

    if args.option == 'receiver':
        os.environ['LD_LIBRARY_PATH'] = path.join(lib_dir)
        cmd = [recv_src, 'recv', args.port]
        check_call(cmd)

    if args.option == 'sender':
        os.environ['LD_LIBRARY_PATH'] = path.join(lib_dir)
        cmd = [send_src, 'send', args.ip, args.port]
        check_call(cmd)


if __name__ == '__main__':
    main()
