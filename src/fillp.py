#!/usr/bin/env python

import sys
import os
from os import path
import string
import random
import shutil
from commands import getstatusoutput
from subprocess import (check_call, Popen)
from src_helpers import (parse_arguments, make_sure_path_exists,
                         check_default_qdisc,wait_and_kill_fillp)
from test.test_helpers import set_sock_bufsizes_for_fillp
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
    output = getstatusoutput("sysctl net.ipv4.udp_mem |awk -F '=' '{print $2}'")  
    output1 = getstatusoutput("sysctl net.core.wmem_max |awk -F '=' '{print $2}'")
    udp_men=output[1].strip().split()
    wmen_max = output1[1].strip().split()
    orgin_udp_men_min = int(udp_men[0])
    orgin_udp_men_default = int(udp_men[1])
    orgin_udp_men_max = int(udp_men[2])
    orgin_wmen_max = int(wmen_max[0])
   
    
    if args.option == 'deps':
        print 'no need iperf'

    if args.option == 'run_first':
        print 'receiver'

    if args.option == 'setup':
        setup_fillp(cc_repo)

    if args.option == 'setup_after_reboot':
        check_default_qdisc('fillp')

    if args.option == 'sender':
        os.environ['LD_LIBRARY_PATH'] = send_path
        set_sock_bufsizes_for_fillp(orgin_udp_men_default, orgin_udp_men_max, orgin_wmen_max)
        cmd = [send_src, '-d', args.ip, '-p', args.port, '-t']
        wait_and_kill_fillp(Popen(cmd),orgin_udp_men_min, orgin_udp_men_max, orgin_udp_men_default,orgin_wmen_max)

    if args.option == 'receiver':
        os.environ['LD_LIBRARY_PATH'] = recv_path
        set_sock_bufsizes_for_fillp(orgin_udp_men_default, orgin_udp_men_max,orgin_wmen_max)
        cmd = [recv_src, '-s', '0.0.0.0', '-p', args.port, '-t']        
        wait_and_kill_fillp(Popen(cmd),orgin_udp_men_min, orgin_udp_men_max, orgin_udp_men_default,orgin_wmen_max)


if __name__ == '__main__':
    main()
