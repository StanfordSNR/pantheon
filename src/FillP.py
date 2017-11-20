#!/usr/bin/env python

import sys
import os
from os import path
import string
import random
import shutil
from subprocess import check_call
from src_helpers import (parse_arguments, make_sure_path_exists,
                         check_default_qdisc)
import project_root

def setup_FillP(cc_repo):
    cmd = ['chmod +x','./server/server']
    check_call(cmd, shell=True, cwd=cc_repo)
    cmd = ['chmod +x','./client/client']
    check_call(cmd, shell=True, cwd=cc_repo)
    cmd = ['sh','udp_config.sh']
    check_call(cmd, shell=True, cwd=cc_repo)
#   os.system('sh ../third_party/FillP/udp_config.sh')	
#    cmd = ['sysclt -w', 'net.ipv4.udp_mem="98304 6291456 6291456"']
#    check_call(cmd, shell=True, cwd=cc_repo)
#    cmd = ['sysclt -w', 'net.core.rmem_default="6291456"']
#    check_call(cmd, shell=True, cwd=cc_repo)
#	cmd = ['sysclt -w', 'net.core.wmem_default="6291456"']
#    check_call(cmd, shell=True, cwd=cc_repo)
#	
#	cmd = ['sysclt -w', 'net.core.rmem_max="6291456"']
#    check_call(cmd, shell=True, cwd=cc_repo)
#    cmd = ['sysclt -w', 'net.core.wmem_max="6291456"']
#    check_call(cmd, shell=True, cwd=cc_repo)
#	cmd = ['sysclt -w', 'net.ipv4.udp_rmem_min="6291456"']
#    check_call(cmd, shell=True, cwd=cc_repo)
#	cmd = ['sysclt -w', 'net.ipv4.udp_wmem_min="6291456"']	
#    check_call(cmd, shell=True, cwd=cc_repo)
#
def main():
    args = parse_arguments('sender_first')

    cc_repo = path.join(project_root.DIR, 'third_party', 'FillP')
    send_src = path.join(cc_repo, 'client', 'client')
    recv_src = path.join(cc_repo, 'server', 'server')
    if args.option == 'deps':
        print 'iperf'

    if args.option == 'run_first':
        print 'sender'

    if args.option == 'setup':
        setup_FillP(cc_repo)

    if args.option == 'setup_after_reboot':
        check_default_qdisc('FillP')

    if args.option == 'sender':
        server_ip = localhost
        os.environ['LD_LIBRARY_PATH'] = cc_repo
        cmd = [send_src, '-s' ,server_ip,'-p',args.port,'-t']
        check_call(cmd)

    if args.option == 'receiver':
        server_ip = localhost
        os.environ['LD_LIBRARY_PATH'] = cc_repo
        cmd = [recv_src, '-d' ,server_ip,'-p',args.port,'-t']
        check_call(cmd)


if __name__ == '__main__':
    main()
