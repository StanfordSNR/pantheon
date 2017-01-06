#!/usr/bin/env python

import os
import sys
import time
import uuid
import signal
import pantheon_helpers
from time import strftime
from os import path
from helpers.parse_arguments import parse_arguments
from helpers.pantheon_help import (Popen, PIPE, check_call, check_output,
                                   parse_remote)


class Test:
    def __init__(self, args):
        self.cc = args.cc.lower()
        self.flows = args.flows
        self.runtime = args.runtime
        self.remote = args.remote
        self.interval = args.interval
        self.server_side = args.server_side
        self.local_addr = args.local_addr
        self.sender_side = args.sender_side
        self.remote_if = args.remote_if
        self.local_if = args.local_if
        self.run_id = args.run_id
        self.downlink_trace = args.downlink_trace
        self.uplink_trace = args.uplink_trace
        self.prepend_mm_cmds = args.prepend_mm_cmds
        self.append_mm_cmds = args.append_mm_cmds
        self.extra_mm_link_args = args.extra_mm_link_args
        self.worst_abs_ofst = None
        self.ntp_addr = args.ntp_addr

    def timeout_handler(self, signum, frame):
        raise

    def get_port(self, process):
        signal.signal(signal.SIGALRM, self.timeout_handler)
        signal.alarm(30)

        try:
            port_info = process.stdout.readline().split(': ')
        except:
            sys.stderr.write('Cannot get port from sender for 30 seconds\n')
            exit(1)
        else:
            signal.alarm(0)

            if port_info[0] == 'Listening on port':
                return port_info[1].strip()
            else:
                return None

    def who_goes_first(self):
        who_goes_first_cmd = ['python', self.src_file, 'who_goes_first']
        who_goes_first_info = check_output(who_goes_first_cmd)
        self.first_to_run = who_goes_first_info.split(' ')[0].lower()

        cond = self.first_to_run == 'receiver' or self.first_to_run == 'sender'
        assert cond, 'Need to specify receiver or sender first'

        self.second_to_run = ('sender' if self.first_to_run == 'receiver'
                              else 'receiver')

    def setup(self):
        self.first_to_run_setup_time = 2

        self.test_dir = path.abspath(path.dirname(__file__))
        src_dir = path.abspath(path.join(self.test_dir, '../src'))
        self.src_file = path.join(src_dir, self.cc + '.py')
        self.tunnel_manager = path.join(self.test_dir, 'tunnel_manager.py')

        # record who goes first
        self.who_goes_first()

        # prepare output logs
        self.datalink_name = self.cc + '_datalink_run%s' % self.run_id
        self.acklink_name = self.cc + '_acklink_run%s' % self.run_id
        self.datalink_log_path = path.join(self.test_dir, self.datalink_name +
                                           '.log')
        self.acklink_log_path = path.join(self.test_dir, self.acklink_name +
                                          '.log')

        if not self.remote:  # local setup
            uplink_trace = os.path.join(self.test_dir, self.uplink_trace)
            downlink_trace = os.path.join(self.test_dir, self.downlink_trace)

            mm_datalink_log = self.cc + '_mm_datalink_run%s.log' % self.run_id
            mm_acklink_log = self.cc + '_mm_acklink_run%s.log' % self.run_id
            self.mm_datalink_log = path.join(self.test_dir, mm_datalink_log)
            self.mm_acklink_log = path.join(self.test_dir, mm_acklink_log)

            if self.first_to_run == 'receiver' or self.flows:
                uplink_log = self.mm_datalink_log
                downlink_log = self.mm_acklink_log
            else:
                uplink_log = self.mm_acklink_log
                downlink_log = self.mm_datalink_log

            self.mm_link_cmd = []

            if self.prepend_mm_cmds:
                self.mm_link_cmd += self.prepend_mm_cmds.split()

            self.mm_link_cmd += [
                'mm-link', uplink_trace, downlink_trace,
                '--uplink-log=' + uplink_log, '--downlink-log=' + downlink_log]

            if self.extra_mm_link_args:
                self.mm_link_cmd += self.extra_mm_link_args.split()

            if self.append_mm_cmds:
                self.mm_link_cmd += self.append_mm_cmds.split()

            self.rd = {}
        else:  # remote setup
            self.rd = parse_remote(self.remote, self.cc)

    # test congestion control without running mm-tunnelclient/mm-tunnelserver
    def run_without_tunnel(self):
        # run the side specified by self.first_to_run
        cmd = ['python', self.src_file, self.first_to_run]
        sys.stderr.write('Running %s %s...\n' % (self.cc, self.first_to_run))
        proc_first = Popen(cmd, stdout=PIPE, preexec_fn=os.setsid)

        # find port printed
        port = None
        while not port:
            port = self.get_port(proc_first)

        # sleep just in case the process isn't quite listening yet
        # the cleaner approach might be to try to verify the socket is open
        time.sleep(self.first_to_run_setup_time)

        self.test_start_time = strftime('%a, %d %b %Y %H:%M:%S %z')
        # run the other side specified by self.second_to_run
        cmd = ('python %s %s $MAHIMAHI_BASE %s' %
               (self.src_file, self.second_to_run, port))
        cmd = ' '.join(self.mm_link_cmd) + " -- sh -c '%s'" % cmd
        sys.stderr.write('Running %s %s...\n' % (self.cc, self.second_to_run))
        proc_second = Popen(cmd, stdout=PIPE, shell=True, preexec_fn=os.setsid)

        signal.signal(signal.SIGALRM, self.timeout_handler)
        signal.alarm(self.runtime)

        try:
            proc_second.communicate()
        except:
            self.test_end_time = strftime('%a, %d %b %Y %H:%M:%S %z')
        else:
            signal.alarm(0)
            sys.stderr.write('Test exited before time limit')
            exit(1)
        finally:
            os.killpg(os.getpgid(proc_first.pid), signal.SIGKILL)
            os.killpg(os.getpgid(proc_second.pid), signal.SIGKILL)

    # read and update worst absolute clock offset
    def update_worst_abs_ofst(self):
        ntp_cmd = [['ntpdate', '-quv', self.ntp_addr]]
        if self.remote:
            cmd = self.rd['ssh_cmd'] + ntp_cmd[0]
            ntp_cmd.append(cmd)

        for cmd in ntp_cmd:
            max_run = 5
            curr_run = 0
            while True:
                curr_run += 1
                if curr_run > max_run:
                    sys.stderr.write('Failed after 5 attempts\n')

                try:
                    ofst = check_output(cmd).rsplit(' ', 2)[-2]
                    ofst = abs(float(ofst)) * 1000
                except:
                    sys.stderr.write('Failed to get clock offset\n')
                else:
                    if not self.worst_abs_ofst or ofst > self.worst_abs_ofst:
                        self.worst_abs_ofst = ofst
                    break

    # test congestion control using mm-tunnelclient/mm-tunnelserver
    def run_with_tunnel(self):
        self.datalink_ingress_logs = []
        self.datalink_egress_logs = []
        self.acklink_ingress_logs = []
        self.acklink_egress_logs = []

        for i in xrange(self.flows):
            tun_id = i + 1
            uid = uuid.uuid4()

            self.datalink_ingress_logs.append(
                '/tmp/pantheon-tmp/%s_flow%s_uid%s.log.ingress'
                % (self.datalink_name, tun_id, uid))
            self.datalink_egress_logs.append(
                '/tmp/pantheon-tmp/%s_flow%s_uid%s.log.egress'
                % (self.datalink_name, tun_id, uid))
            self.acklink_ingress_logs.append(
                '/tmp/pantheon-tmp/%s_flow%s_uid%s.log.ingress'
                % (self.acklink_name, tun_id, uid))
            self.acklink_egress_logs.append(
                '/tmp/pantheon-tmp/%s_flow%s_uid%s.log.egress'
                % (self.acklink_name, tun_id, uid))

        if self.remote and self.ntp_addr:
            self.update_worst_abs_ofst()

        # run mm-tunnelserver manager
        if self.remote:
            if self.server_side == 'local':
                ts_manager_cmd = ['python', self.tunnel_manager]
            else:
                ts_manager_cmd = self.rd['ssh_cmd'] + [
                    'python', self.rd['tun_manager']]
        else:
            ts_manager_cmd = ['python', self.tunnel_manager]

        sys.stderr.write('[tunnel server manager (tsm)] ')
        ts_manager = Popen(ts_manager_cmd, stdin=PIPE,
                           stdout=PIPE, preexec_fn=os.setsid)

        while True:
            running = ts_manager.stdout.readline()
            if 'tunnel manager is running' in running:
                sys.stderr.write(running)
                break

        ts_manager.stdin.write('prompt [tsm]\n')

        # run mm-tunnelclient manager
        if self.remote:
            if self.server_side == 'local':
                tc_manager_cmd = self.rd['ssh_cmd'] + [
                    'python', self.rd['tun_manager']]
            else:
                tc_manager_cmd = ['python', self.tunnel_manager]
        else:
            tc_manager_cmd = self.mm_link_cmd + ['python', self.tunnel_manager]

        sys.stderr.write('[tunnel client manager (tcm)] ')
        tc_manager = Popen(tc_manager_cmd, stdin=PIPE,
                           stdout=PIPE, preexec_fn=os.setsid)

        while True:
            running = tc_manager.stdout.readline()
            if 'tunnel manager is running' in running:
                sys.stderr.write(running)
                break

        tc_manager.stdin.write('prompt [tcm]\n')

        # create alias for ts_manager and tc_manager using sender or receiver
        if self.sender_side == self.server_side:
            send_manager = ts_manager
            recv_manager = tc_manager
        else:
            send_manager = tc_manager
            recv_manager = ts_manager

        # run each flow
        second_cmds = []
        for i in xrange(self.flows):
            tun_id = i + 1
            readline_cmd = 'tunnel %s readline\n' % tun_id

            # run mm-tunnelserver
            if self.server_side == self.sender_side:
                ts_cmd = ('mm-tunnelserver --ingress-log=%s --egress-log=%s' %
                          (self.acklink_ingress_logs[i],
                           self.datalink_egress_logs[i]))
            else:
                ts_cmd = ('mm-tunnelserver --ingress-log=%s --egress-log=%s' %
                          (self.datalink_ingress_logs[i],
                           self.acklink_egress_logs[i]))

            if self.server_side == 'remote':
                if self.remote_if:
                    ts_cmd += ' --interface=' + self.remote_if
            else:
                if self.local_if:
                    ts_cmd += ' --interface=' + self.local_if

            ts_cmd = 'tunnel %s %s\n' % (tun_id, ts_cmd)

            ts_manager.stdin.write(ts_cmd)

            # read the command from mm-tunnelserver to run mm-tunnelclient
            ts_manager.stdin.write(readline_cmd)

            cmd = ts_manager.stdout.readline().split()
            if self.server_side == 'remote':
                cmd[1] = self.rd.get('ip', '$MAHIMAHI_BASE')
            else:
                cmd[1] = self.local_addr
            tc_pri_ip = cmd[3]  # tunnel client private IP
            ts_pri_ip = cmd[4]  # tunnel server private IP

            if self.sender_side == self.server_side:
                send_pri_ip = ts_pri_ip
                recv_pri_ip = tc_pri_ip
            else:
                send_pri_ip = tc_pri_ip
                recv_pri_ip = ts_pri_ip

            # run mm-tunnelclient
            if self.server_side == self.sender_side:
                tc_cmd = ('%s --ingress-log=%s --egress-log=%s' %
                          (' '.join(cmd), self.datalink_ingress_logs[i],
                           self.acklink_egress_logs[i]))
            else:
                tc_cmd = ('%s --ingress-log=%s --egress-log=%s' %
                          (' '.join(cmd), self.acklink_ingress_logs[i],
                           self.datalink_egress_logs[i]))

            if self.server_side == 'remote':
                if self.local_if:
                    tc_cmd += ' --interface=' + self.local_if
            else:
                if self.remote_if:
                    tc_cmd += ' --interface=' + self.remote_if

            tc_cmd = 'tunnel %s %s\n' % (tun_id, tc_cmd)

            # re-run mm-tunnelclient after 20s timeout for at most 3 times
            max_run = 3
            curr_run = 0
            got_connection = ''
            while 'got connection' not in got_connection:
                curr_run += 1
                if curr_run > max_run:
                    sys.stderr.write('Cannot establish tunnel\n')
                    exit(1)

                tc_manager.stdin.write(tc_cmd)
                while True:
                    tc_manager.stdin.write(readline_cmd)

                    signal.signal(signal.SIGALRM, self.timeout_handler)
                    signal.alarm(20)

                    try:
                        got_connection = tc_manager.stdout.readline()
                        sys.stderr.write('Tunnel is connected\n')
                    except:
                        sys.stderr.write('Tunnel connection timeout\n')
                        break
                    else:
                        signal.alarm(0)
                        if 'got connection' in got_connection:
                            break

            if self.first_to_run == 'receiver':
                if self.sender_side == 'local':
                    first_src_file = self.rd.get('cc_src', self.src_file)
                    second_src_file = self.src_file
                else:
                    first_src_file = self.src_file
                    second_src_file = self.rd.get('cc_src', self.src_file)

                first_cmd = ('tunnel %s python %s receiver\n' %
                             (tun_id, first_src_file))
                second_cmd = ('tunnel %s python %s sender %s' %
                              (tun_id, second_src_file, recv_pri_ip))

                recv_manager.stdin.write(first_cmd)

                # find printed port
                port = None
                while not port:
                    recv_manager.stdin.write(readline_cmd)
                    port = self.get_port(recv_manager)

                second_cmd += ' %s\n' % port
                second_cmds.append(second_cmd)
            else:  # self.first_to_run == 'sender'
                if self.sender_side == 'local':
                    first_src_file = self.src_file
                    second_src_file = self.rd.get('cc_src', self.src_file)
                else:
                    first_src_file = self.rd.get('cc_src', self.src_file)
                    second_src_file = self.src_file

                first_cmd = ('tunnel %s python %s sender\n' %
                             (tun_id, first_src_file))
                second_cmd = ('tunnel %s python %s receiver %s' %
                              (tun_id, second_src_file, send_pri_ip))

                send_manager.stdin.write(first_cmd)

                # find printed port
                port = None
                while not port:
                    send_manager.stdin.write(readline_cmd)
                    port = self.get_port(send_manager)

                second_cmd += ' %s\n' % port
                second_cmds.append(second_cmd)

        time.sleep(self.first_to_run_setup_time)

        start_time = time.time()
        self.test_start_time = strftime('%a, %d %b %Y %H:%M:%S %z')
        # start each flow self.interval seconds after the previous one
        for i in xrange(len(second_cmds)):
            if i != 0:
                time.sleep(self.interval)
            second_cmd = second_cmds[i]
            if self.first_to_run == 'receiver':
                send_manager.stdin.write(second_cmd)
            else:
                recv_manager.stdin.write(second_cmd)
        elapsed_time = time.time() - start_time
        assert self.runtime > elapsed_time, (
            'interval time between flows is too long')
        time.sleep(self.runtime - elapsed_time)

        # stop all the running flows and quit tunnel managers
        ts_manager.stdin.write('halt\n')
        tc_manager.stdin.write('halt\n')

        self.test_end_time = strftime('%a, %d %b %Y %H:%M:%S %z')

        if self.remote and self.ntp_addr:
            self.update_worst_abs_ofst()

        self.merge_tunnel_logs()

    def merge_tunnel_logs(self):
        datalink_tun_logs = []
        acklink_tun_logs = []

        for i in xrange(self.flows):
            tun_id = i + 1
            if self.remote:
                # download logs from remote side
                scp_cmd = 'scp -C %s:' % self.rd['addr']
                scp_cmd += '%(log)s %(log)s'

                if self.sender_side == 'remote':
                    check_call(scp_cmd % {'log': self.acklink_ingress_logs[i]},
                               shell=True)
                    check_call(scp_cmd % {'log': self.datalink_egress_logs[i]},
                               shell=True)
                else:
                    check_call(scp_cmd % {'log':
                                          self.datalink_ingress_logs[i]},
                               shell=True)
                    check_call(scp_cmd % {'log': self.acklink_egress_logs[i]},
                               shell=True)

            uid = uuid.uuid4()
            datalink_tun_log = (
                '/tmp/pantheon-tmp/%s_flow%s_uid%s.log.merged'
                % (self.datalink_name, tun_id, uid))
            acklink_tun_log = (
                '/tmp/pantheon-tmp/%s_flow%s_uid%s.log.merged'
                % (self.acklink_name, tun_id, uid))

            cmd = ['merge-tunnel-logs', 'single', '-i',
                   self.datalink_ingress_logs[i], '-e',
                   self.datalink_egress_logs[i], '-o', datalink_tun_log]
            check_call(cmd)

            cmd = ['merge-tunnel-logs', 'single', '-i',
                   self.acklink_ingress_logs[i], '-e',
                   self.acklink_egress_logs[i], '-o', acklink_tun_log]
            check_call(cmd)

            datalink_tun_logs.append(datalink_tun_log)
            acklink_tun_logs.append(acklink_tun_log)

        cmd = ['merge-tunnel-logs', 'multiple', '-o', self.datalink_log_path]
        if not self.remote:
            cmd += ['--link-log', self.mm_datalink_log]
        cmd += datalink_tun_logs
        check_call(cmd)

        cmd = ['merge-tunnel-logs', 'multiple', '-o', self.acklink_log_path]
        if not self.remote:
            cmd += ['--link-log', self.mm_acklink_log]
        cmd += acklink_tun_logs

        check_call(cmd)

    def run_congestion_control(self):
        self.run_with_tunnel() if self.flows else self.run_without_tunnel()

    def record_time_stats(self):
        stats_log = path.join(self.test_dir,
                              '%s_stats_run%s.log' % (self.cc, self.run_id))
        stats = open(stats_log, 'w')

        # save start time and end time of test
        test_run_duration = (
            'Start at: %s\nEnd at: %s\n' %
            (self.test_start_time, self.test_end_time))
        sys.stderr.write(test_run_duration)
        stats.write(test_run_duration)

        if self.worst_abs_ofst:
            offset_info = ('Worst absolute clock offset: %s ms\n'
                           % self.worst_abs_ofst)
            sys.stderr.write(offset_info)
            stats.write(offset_info)

        stats.close()

        sys.stderr.write('Done\n\n')

    # congestion control test
    def test(self):
        # local or remote setup before running tests
        self.setup()

        # run receiver and sender
        self.run_congestion_control()

        # write runtimes and clock offsets to file
        self.record_time_stats()


def main():
    args = parse_arguments(path.basename(__file__))

    test = Test(args)
    test.test()


if __name__ == '__main__':
    DEVNULL = open(os.devnull, 'w')
    main()
    DEVNULL.close()
