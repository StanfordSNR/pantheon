#!/usr/bin/env python

import sys
import os
from os import path
import string
import random
import shutil
from subprocess import check_call Popen
from src_helpers import (parse_arguments, make_sure_path_exists,
                         check_default_qdisc)
from test.test_helpers import set_sock_bufsizes_for_fillp
import project_root

def setup_fillp(cc_repo):
    cmd = ['sudo chmod +x','./server/server']
    check_call(cmd, shell=True, cwd=cc_repo)
    cmd = ['sudo chmod +x','./client/client']
    check_call(cmd, shell=True, cwd=cc_repo)
    if orgin_udp_men_default >= 62914560 and orgin_udp_men_max >= 62914560:
        pass
    else:
        cmd = ['sudo sysctl -w','net.ipv4.udp_mem="98304 62914560 62914560"']
        check_call(cmd, shell=True, cwd=cc_repo)
        
def wait_and_kill_fillp(proc):
    time.sleep(35)
    os.kill(proc.pid, signal.SIGKILL)
    cmd = ['sysctl -w','net.ipv4.udp_mem="%s %s %s" % (orgin_udp_men_min ,orgin_udp_men_max ,orgin_udp_men_default)']
    check_call(cmd, shell=True, cwd=cc_repo)
             
def main():
    args = parse_arguments('receiver_first')

    cc_repo = path.join(project_root.DIR, 'third_party', 'fillp')
    send_src = path.join(cc_repo, 'client', 'client')
    recv_src = path.join(cc_repo, 'server', 'server')
    cmd = ["sysctl net.ipv4.udp_mem","|awk -F '=' '{print $2}'",'awk -F ' ' '{print $2}'']
    output = Popen(cmd,stdout=subprocess.PIPE,shell=True).communicate()
    orgin_udp_men_default = output[0]
    cmd = ["sysctl net.ipv4.udp_mem","|awk -F '=' '{print $2}'",'awk -F ' ' '{print $3}'']
    output = Popen(cmd,stdout=subprocess.PIPE,shell=True).communicate()
    orgin_udp_men_max = output[0]
    cmd = ["sysctl net.ipv4.udp_mem","|awk -F '=' '{print $2}'",'awk -F ' ' '{print $1}'']
    output = Popen(cmd,stdout=subprocess.PIPE,shell=True).communicate()
    orgin_udp_men_min = output[0]
    if args.option == 'deps':
        print 'iperf'

    if args.option == 'run_first':
        print 'receiver'

    if args.option == 'setup':
        setup_fillp(cc_repo)

    if args.option == 'setup_after_reboot':
        cmd = ['sysctl -w','net.ipv4.udp_mem="98304 62914560 62914560"']
        check_call(cmd, shell=True, cwd=cc_repo)
        check_default_qdisc('fillp')

    if args.option == 'sender':
        os.environ['LD_LIBRARY_PATH'] = cc_repo
        cmd = [send_src, '-s' ,args.ip,'-p',args.port,'-t']
        wait_and_kill_fillp(Popen(cmd))

    if args.option == 'receiver':
        server_ip = 'localhost'
        os.environ['LD_LIBRARY_PATH'] = cc_repo
        cmd = [recv_src, '-d' ,server_ip,'-p',args.port,'-t']        
        wait_and_kill_fillp(Popen(cmd))


if __name__ == '__main__':
    main()
