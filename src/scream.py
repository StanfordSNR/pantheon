#!/usr/bin/env python

from os import path
from subprocess import check_call
import project_root
from helpers import (
    get_open_port, print_port_for_tests, parse_arguments, apply_patch)


def main():
    args = parse_arguments('receiver_first')

    cc_repo = path.join(project_root.DIR, 'third_party', 'scream')
    scream_dir = path.join(project_root.DIR, 'src', 'scream')
    recv_src = path.join(scream_dir, 'ScreamServer')
    send_src = path.join(scream_dir, 'ScreamClient')

    if args.option == 'deps':
        print 'dh-autoreconf'

    if args.option == 'run_first':
        print 'receiver'

    if args.option == 'setup':
        # apply patch to add header cmath
        apply_patch('scream.patch', cc_repo)

        sh_cmd = './autogen.sh && ./configure && make -j2'
        sourdough_dir = path.join(project_root.DIR, 'third_party', 'sourdough')
        check_call(sh_cmd, shell=True, cwd=sourdough_dir)
        check_call(sh_cmd, shell=True, cwd=scream_dir)

    if args.option == 'receiver':
        port = get_open_port()
        print_port_for_tests(port)

        cmd = [recv_src, port]
        check_call(cmd)

    if args.option == 'sender':
        cmd = [send_src, args.ip, args.port]
        check_call(cmd)


if __name__ == '__main__':
    main()
