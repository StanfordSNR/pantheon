#!/usr/bin/env python

import os
import sys
import unittest
import time
import signal
from parse_arguments import parse_arguments
from os import path
from subprocess_wrapper import Popen, PIPE, check_call, check_output


class TestCongestionControl(unittest.TestCase):
    def __init__(self, test_name, args):
        super(TestCongestionControl, self).__init__(test_name)
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

    def timeout_handler(signum, frame):
        raise

    def get_port(self, process):
        port_info = process.stdout.readline().split(': ')
        if port_info[0] == 'Listening on port':
            return port_info[1].strip()
        else:
            return None

    def who_goes_first(self):
        who_goes_first_cmd = ['python', self.src_file, 'who_goes_first']
        who_goes_first_info = check_output(who_goes_first_cmd)
        self.first_to_run = who_goes_first_info.split(' ')[0].lower()
        self.assertTrue(
            self.first_to_run == 'receiver' or self.first_to_run == 'sender',
            msg='Need to specify receiver or sender first')
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
        datalink_log = self.cc + '_datalink_run%s.log' % self.run_id
        acklink_log = self.cc + '_acklink_run%s.log' % self.run_id
        self.datalink_log = path.join(self.test_dir, datalink_log)
        self.acklink_log = path.join(self.test_dir, acklink_log)

        if not self.remote:  # local setup
            uplink_trace = os.path.join(self.test_dir, '12mbps_trace')
            downlink_trace = os.path.join(self.test_dir, '12mbps_trace')

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

            self.mm_link_cmd = [
                'mm-link', uplink_trace, downlink_trace,
                '--uplink-log=' + uplink_log, '--downlink-log=' + downlink_log]
            self.remote_ip = '$MAHIMAHI_BASE'
            self.remote_src_file = self.src_file
        else:  # remote setup
            (self.remote_addr, self.remote_dir) = self.remote.split(':')
            self.ssh_cmd = ['ssh', self.remote_addr]
            self.remote_ip = self.remote_addr.split('@')[-1]

            remote_src_dir = path.join(self.remote_dir, 'src')
            self.remote_src_file = path.join(remote_src_dir, self.cc + '.py')

            remote_test_dir = path.join(self.remote_dir, 'test')
            self.remote_tunnel_manager = path.join(remote_test_dir,
                                                   'tunnel_manager.py')

    # test congestion control without running mm-tunnelclient/mm-tunnelserver
    def run_without_tunnel(self):
        # run the side specified by self.first_to_run
        cmd = ['python', self.remote_src_file, self.first_to_run]
        sys.stderr.write('Running %s %s...\n' % (self.cc, self.first_to_run))
        proc_first = Popen(cmd, stdout=PIPE, preexec_fn=os.setsid)

        # find port printed
        port = None
        while not port:
            port = self.get_port(proc_first)

        # sleep just in case the process isn't quite listening yet
        # the cleaner approach might be to try to verify the socket is open
        time.sleep(self.first_to_run_setup_time)

        # run the other side specified by self.second_to_run
        cmd = ('python %s %s %s %s' %
               (self.src_file, self.second_to_run, self.remote_ip, port))
        cmd = ' '.join(self.mm_link_cmd) + " -- sh -c '%s'" % cmd
        sys.stderr.write('Running %s %s...\n' % (self.cc, self.second_to_run))
        proc_second = Popen(cmd, stdout=PIPE, shell=True, preexec_fn=os.setsid)

        signal.signal(signal.SIGALRM, self.timeout_handler)
        signal.alarm(self.runtime)

        try:
            proc_second.communicate()
        except:
            sys.stderr.write('Done\n')
        else:
            self.fail('Test exited before time limit')
        finally:
            os.killpg(os.getpgid(proc_first.pid), signal.SIGKILL)
            os.killpg(os.getpgid(proc_second.pid), signal.SIGKILL)

    # read ntpdate offset
    def read_ntp_offset(self, tun_manager):
        ntp_cmd = 'ntpdate -quv pool.ntp.org\n'
        tun_manager.stdin.write(ntp_cmd)
        offset = tun_manager.stdout.readline().strip()
        if offset == 'error':
            return None
        else:
            return float(offset) * 1000

    # test congestion control using mm-tunnelclient/mm-tunnelserver
    def run_with_tunnel(self):
        # ts: mm-tunnelserver  tc: mm-tunnelclient
        # prepare ingress and egress logs
        self.ts_ilogs = []
        self.ts_elogs = []
        self.tc_ilogs = []
        self.tc_elogs = []

        for i in xrange(self.flows):
            tun_id = i + 1
            self.ts_ilogs.append('/tmp/tunserver%s_ingress.log' % tun_id)
            self.ts_elogs.append('/tmp/tunserver%s_egress.log' % tun_id)
            self.tc_ilogs.append('/tmp/tunclient%s_ingress.log' % tun_id)
            self.tc_elogs.append('/tmp/tunclient%s_egress.log' % tun_id)

        # run mm-tunnelserver manager
        if self.remote:
            if self.server_side == 'local':
                ts_manager_cmd = ['python', self.tunnel_manager]
            else:
                ts_manager_cmd = self.ssh_cmd + ['python',
                                                 self.remote_tunnel_manager]
        else:
            ts_manager_cmd = ['python', self.tunnel_manager]

        sys.stderr.write('[tunnel server manager (tsm)] ')
        ts_manager = Popen(ts_manager_cmd, stdin=PIPE,
                           stdout=PIPE, preexec_fn=os.setsid)
        ts_manager.stdin.write('prompt [tsm]\n')

        # run mm-tunnelclient manager
        if self.remote:
            if self.server_side == 'local':
                tc_manager_cmd = self.ssh_cmd + ['python',
                                                 self.remote_tunnel_manager]
            else:
                tc_manager_cmd = ['python', self.tunnel_manager]
        else:
            tc_manager_cmd = self.mm_link_cmd + ['python', self.tunnel_manager]

        sys.stderr.write('[tunnel client manager (tcm)] ')
        tc_manager = Popen(tc_manager_cmd, stdin=PIPE,
                           stdout=PIPE, preexec_fn=os.setsid)
        tc_manager.stdin.write('prompt [tcm]\n')

        # create alias for ts_manager and tc_manager using local or remote
        if self.server_side == 'local':
            local_manager = ts_manager
            remote_manager = tc_manager
        else:
            local_manager = tc_manager
            remote_manager = ts_manager

        # create alias for ts_manager and tc_manager using sender or receiver
        if self.sender_side == self.server_side:
            send_manager = ts_manager
            recv_manager = tc_manager
        else:
            send_manager = tc_manager
            recv_manager = ts_manager

        # read ntpdate offsets
        if self.remote:
            self.ofst_local_start = self.read_ntp_offset(local_manager)
            self.ofst_remote_start = self.read_ntp_offset(remote_manager)

        # run each flow
        second_cmds = []
        for i in xrange(self.flows):
            tun_id = i + 1
            readline_cmd = 'tunnel %s readline\n' % tun_id

            # run mm-tunnelserver
            ts_cmd = ('mm-tunnelserver --ingress-log=%s --egress-log=%s' %
                      (self.ts_ilogs[i], self.ts_elogs[i]))

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
                cmd[1] = self.remote_ip
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
            tc_cmd = ('%s --ingress-log=%s --egress-log=%s' %
                      (' '.join(cmd), self.tc_ilogs[i], self.tc_elogs[i]))

            if self.server_side == 'remote':
                if self.local_if:
                    tc_cmd += ' --interface=' + self.local_if
            else:
                if self.remote_if:
                    tc_cmd += ' --interface=' + self.remote_if

            tc_cmd = 'tunnel %s %s\n' % (tun_id, tc_cmd)
            tc_manager.stdin.write(tc_cmd)

            if self.first_to_run == 'receiver':
                if self.sender_side == 'local':
                    first_src_file = self.remote_src_file
                    second_src_file = self.src_file
                else:
                    first_src_file = self.src_file
                    second_src_file = self.remote_src_file

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
                    second_src_file = self.remote_src_file
                else:
                    first_src_file = self.remote_src_file
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
        self.assertTrue(self.runtime > elapsed_time,
                        'interval time between flows is too long')
        time.sleep(self.runtime - elapsed_time)

        # read ntpdate offsets
        if self.remote:
            self.ofst_local_end = self.read_ntp_offset(local_manager)
            self.ofst_remote_end = self.read_ntp_offset(remote_manager)

        # stop all the running flows
        ts_manager.stdin.write('halt\n')
        tc_manager.stdin.write('halt\n')

        self.merge_tunnel_logs()
        sys.stderr.write('Done\n')

    def merge_tunnel_logs(self):
        datalink_tun_logs = []
        acklink_tun_logs = []

        for i in xrange(self.flows):
            tun_id = i + 1
            if self.remote:
                # download logs from remote side
                scp_cmd = 'scp -C %s:' % self.remote_addr
                scp_cmd += '%(log)s %(log)s'

                if self.server_side == 'remote':
                    check_call(scp_cmd % {'log': self.ts_ilogs[i]}, shell=True)
                    check_call(scp_cmd % {'log': self.ts_elogs[i]}, shell=True)
                else:
                    check_call(scp_cmd % {'log': self.tc_ilogs[i]}, shell=True)
                    check_call(scp_cmd % {'log': self.tc_elogs[i]}, shell=True)

            datalink_tun_log = '/tmp/datalink_tun%s.log' % tun_id
            acklink_tun_log = '/tmp/acklink_tun%s.log' % tun_id
            if self.sender_side == self.server_side:
                s2c_log = datalink_tun_log
                c2s_log = acklink_tun_log
            else:
                s2c_log = acklink_tun_log
                c2s_log = datalink_tun_log

            cmd = ['mm-tunnel-merge-logs', 'single', '-i', self.ts_ilogs[i],
                   '-e', self.tc_elogs[i], '-o', c2s_log]
            check_call(cmd)

            cmd = ['mm-tunnel-merge-logs', 'single', '-i', self.tc_ilogs[i],
                   '-e', self.ts_elogs[i], '-o', s2c_log]
            check_call(cmd)

            datalink_tun_logs.append(datalink_tun_log)
            acklink_tun_logs.append(acklink_tun_log)

        cmd = ['mm-tunnel-merge-logs', 'multiple', '-o', self.datalink_log]
        if not self.remote:
            cmd += ['--link-log', self.mm_datalink_log]
        cmd += datalink_tun_logs
        check_call(cmd)

        cmd = ['mm-tunnel-merge-logs', 'multiple', '-o', self.acklink_log]
        if not self.remote:
            cmd += ['--link-log', self.mm_acklink_log]
        cmd += acklink_tun_logs
        check_call(cmd)

    def run_congestion_control(self):
        self.run_with_tunnel() if self.flows else self.run_without_tunnel()

    def gen_results(self):
        throughput_cmd = 'mm-tunnel-throughput'
        delay_cmd = 'mm-tunnel-delay'

        if self.flows:
            datalink_log = self.datalink_log
            acklink_log = self.acklink_log
        else:
            datalink_log = self.mm_datalink_log
            acklink_log = self.mm_acklink_log

        datalink_throughput_png = path.join(
            self.test_dir,
            '%s_datalink_throughput_run%s.png' % (self.cc, self.run_id))
        datalink_delay_png = path.join(
            self.test_dir,
            '%s_datalink_delay_run%s.png' % (self.cc, self.run_id))
        acklink_throughput_png = path.join(
            self.test_dir,
            '%s_acklink_throughput_run%s.png' % (self.cc, self.run_id))
        acklink_delay_png = path.join(
            self.test_dir,
            '%s_acklink_delay_run%s.png' % (self.cc, self.run_id))

        stats_log = path.join(self.test_dir,
                              '%s_stats_run%s.log' % (self.cc, self.run_id))
        stats = open(stats_log, 'w')

        sys.stderr.write('\n')
        # Data link
        # throughput
        datalink_throughput = open(datalink_throughput_png, 'w')
        cmd = [throughput_cmd, '500', datalink_log]

        sys.stderr.write('* Data link statistics:\n')
        stats.write('* Data link statistics:\n')

        proc = Popen(cmd, stdout=datalink_throughput, stderr=PIPE)
        datalink_results = proc.communicate()[1]
        sys.stderr.write(datalink_results)
        stats.write(datalink_results)

        datalink_throughput.close()
        self.assertEqual(proc.returncode, 0)

        # delay
        datalink_delay = open(datalink_delay_png, 'w')
        cmd = [delay_cmd, datalink_log]

        proc = Popen(cmd, stdout=datalink_delay, stderr=DEVNULL)
        proc.communicate()

        datalink_delay.close()
        self.assertEqual(proc.returncode, 0)

        sys.stderr.write('\n')
        # ACK link
        # throughput
        acklink_throughput = open(acklink_throughput_png, 'w')
        cmd = [throughput_cmd, '500', acklink_log]

        sys.stderr.write('* ACK link statistics:\n')
        stats.write('* ACK link statistics:\n')

        proc = Popen(cmd, stdout=acklink_throughput, stderr=PIPE)
        acklink_results = proc.communicate()[1]
        sys.stderr.write(acklink_results)
        stats.write(acklink_results)

        acklink_throughput.close()
        self.assertEqual(proc.returncode, 0)

        # delay
        acklink_delay = open(acklink_delay_png, 'w')
        cmd = [delay_cmd, acklink_log]

        proc = Popen(cmd, stdout=acklink_delay, stderr=DEVNULL)
        proc.communicate()

        acklink_delay.close()
        self.assertEqual(proc.returncode, 0)

        if (self.remote and self.ofst_local_start and self.ofst_local_end and
                self.ofst_remote_start and self.ofst_remote_end):
            offset_info = (
                '* Clock offsets:\n'
                '-- Before test:\n'
                'Local clock offset: %s ms\n'
                'Remote clock offset: %s ms\n'
                '-- After test:\n'
                'Local clock offset: %s ms\n'
                'Remote clock offset: %s ms\n'
                % (self.ofst_local_start, self.ofst_local_end,
                   self.ofst_remote_start, self.ofst_remote_end))
            stats.write(offset_info)

        stats.close()

    # congestion control test
    def test_congestion_control(self):
        # local or remote setup before running tests
        self.setup()

        # run receiver and sender
        self.run_congestion_control()

        # generate results, including statistics and graphs
        self.gen_results()


def main():
    args = parse_arguments(path.basename(__file__))

    # create test suite to run
    suite = unittest.TestSuite()
    suite.addTest(TestCongestionControl('test_congestion_control', args))
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)


if __name__ == '__main__':
    DEVNULL = open(os.devnull, 'w')
    main()
    DEVNULL.close()
