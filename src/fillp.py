#!/usr/bin/env python

import sys
import os
from os import path
import string
import random
import shutil
from subprocess import (check_call, Popen)
from src_helpers import (parse_arguments, make_sure_path_exists,
                         check_default_qdisc)
import project_root


def setup_fillp(cc_repo):
    cmd = ['sudo chmod +x ./server/server']
    check_call(cmd, shell=True, cwd=cc_repo)
    cmd = ['sudo chmod +x ./client/client']
    check_call(cmd, shell=True, cwd=cc_repo)

    
def main():
    args = parse_arguments('receiver_first')
    
    cc_repo = path.join(project_root.DIR, 'third_party', 'fillp')
    send_src = path.join(cc_repo, 'client', 'client')
    recv_src = path.join(cc_repo, 'server', 'server')
    send_path = path.join(cc_repo, 'client')
    recv_path = path.join(cc_repo, 'server')
     
    if args.option == 'run_first':
        print 'receiver'
        
    if args.option == 'setup':
        setup_fillp(cc_repo)

    if args.option == 'setup_after_reboot':
        check_default_qdisc('fillp')

    if args.option == 'sender':
        os.environ['LD_LIBRARY_PATH'] = send_path
        cmd = [send_src, '-d', args.ip, '-p', args.port, '-t']
        Popen(cmd)

    if args.option == 'receiver':
        os.environ['LD_LIBRARY_PATH'] = recv_path
        cmd = [recv_src, '-s', '0.0.0.0', '-p', args.port, '-t']        
        Popen(cmd)


if __name__ == '__main__':
    main()
