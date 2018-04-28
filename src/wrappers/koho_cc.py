#!/usr/bin/env python

from os import path
from subprocess import check_call
from src_helpers import parse_arguments, apply_patch, check_default_qdisc
import project_root


def main():
    args = parse_arguments('receiver_first')

    cc_repo = path.join(project_root.DIR, 'third_party', 'koho_cc')
    recv_src = path.join(cc_repo, 'datagrump', 'receiver')
    send_src = path.join(cc_repo, 'datagrump', 'sender')

    if args.option == 'run_first':
        print 'receiver'

    if args.option == 'setup':
        # apply patch to reduce MTU size
        apply_patch('koho_cc.patch', cc_repo)

        sh_cmd = './autogen.sh && ./configure && make -j2'
        check_call(sh_cmd, shell=True, cwd=cc_repo)

    if args.option == 'setup_after_reboot':
        check_default_qdisc('koho_cc')

    if args.option == 'receiver':
        cmd = [recv_src, args.port]
        check_call(cmd)

    if args.option == 'sender':
        cmd = [send_src, args.ip, args.port]
        check_call(cmd)


if __name__ == '__main__':
    main()
