#!/usr/bin/env python

import sys
import os
from os import path
import string
import random
import shutil
from subprocess import (check_call, Popen)
from src_helpers import (parse_arguments, make_sure_path_exists,
                         check_default_qdisc,wait_and_kill_fillp)
from test.test_helpers import set_sock_bufsizes_for_fillp
import project_root

def setup_fillp(cc_repo):
    cmd = ['sudo chmod +x','./server/server']
    check_call(cmd, shell=True, cwd=cc_repo)
    cmd = ['sudo chmod +x','./client/client']
    check_call(cmd, shell=True, cwd=cc_repo)

def main():
    args = parse_arguments('receiver_first')

    cc_repo = path.join(project_root.DIR, 'third_party', 'fillp')
    send_src = path.join(cc_repo, 'client', 'client')
    recv_src = path.join(cc_repo, 'server', 'server')
    cmd = ["sysctl net.ipv4.udp_mem","|awk -F '=' '{print $2}'"]
    output = Popen(cmd,stdout=subprocess.PIPE,shell=True).communicate()
    udp_men=output[0].split()
    orgin_udp_men_min = udp_men[0]
    orgin_udp_men_default = udp_men[1]
    orgin_udp_men_max = oudp_menu[2]
   
    
    if args.option == 'deps':
        print 'iperf'

    if args.option == 'run_first':
        print 'receiver'

    if args.option == 'setup':
        setup_fillp(cc_repo)

    if args.option == 'setup_after_reboot':
        check_default_qdisc('fillp')

    if args.option == 'sender':
        os.environ['LD_LIBRARY_PATH'] = cc_repo
        set_sock_bufsizes_for_fillp(orgin_udp_men_default, orgin_udp_men_max)
        cmd = [send_src, '-s' ,args.ip,'-p',args.port,'-t']
        wait_and_kill_fillp(Popen(cmd),orgin_udp_men_min, orgin_udp_men_max, orgin_udp_men_default)

    if args.option == 'receiver':
        os.environ['LD_LIBRARY_PATH'] = cc_repo
        set_sock_bufsizes_for_fillp(orgin_udp_men_default, orgin_udp_men_max)
        cmd = [recv_src, '-d' ,'localhost','-p',args.port,'-t']        
        wait_and_kill_fillp(Popen(cmd),orgin_udp_men_min, orgin_udp_men_max, orgin_udp_men_default)


if __name__ == '__main__':
    main()
