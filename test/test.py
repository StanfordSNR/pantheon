#!/usr/bin/python

import os
import sys
import unittest
import time
import signal
from parse_arguments import parse_arguments
from os import path
from subprocess import Popen, PIPE, check_call, check_output


class TestCongestionControl(unittest.TestCase):
    def __init__(self, test_name, args):
        super(TestCongestionControl, self).__init__(test_name)
        self.cc = args.cc.lower()
        self.flows = args.flows
        self.remote = args.remote
        self.runtime = args.runtime
        self.private_key = args.private_key

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
        sys.stderr.write('+ ' + ' '.join(who_goes_first_cmd) + '\n')
        who_goes_first_info = check_output(who_goes_first_cmd)
        self.first_to_run = who_goes_first_info.split(' ')[0].lower()
        self.assertTrue(
            self.first_to_run == 'receiver' or self.first_to_run == 'sender',
            msg='Need to specify receiver or sender first')
        self.second_to_run = ('sender' if self.first_to_run == 'receiver'
                              else 'receiver')

    def setup(self):
        self.first_to_run_setup_time = 1

        self.test_dir = path.abspath(path.dirname(__file__))
        src_dir = path.abspath(path.join(self.test_dir, '../src'))
        self.src_file = path.join(src_dir, self.cc + '.py')
        self.tunnel_manager = path.join(self.test_dir, 'tunnel_manager.py')

        # record who goes first
        self.who_goes_first()

        # prepare output logs
        self.datalink_log = path.join(self.test_dir, self.cc + '_datalink.log')
        self.acklink_log = path.join(self.test_dir, self.cc + '_acklink.log')
        if self.flows:
            self.tun_datalink_log = path.join(self.test_dir, self.cc +
                                              '_tun_datalink.log')
            self.tun_acklink_log = path.join(self.test_dir, self.cc +
                                             '_tun_acklink.log')

        if not self.remote:  # local setup
            traces_dir = '/usr/share/mahimahi/traces/'
            if self.first_to_run == 'receiver' or self.flows:
                self.uplink_trace = traces_dir + 'Verizon-LTE-short.up'
                self.downlink_trace = traces_dir + 'Verizon-LTE-short.down'
                self.uplink_log = self.datalink_log
                self.downlink_log = self.acklink_log
            else:
                self.uplink_trace = traces_dir + 'Verizon-LTE-short.down'
                self.downlink_trace = traces_dir + 'Verizon-LTE-short.up'
                self.uplink_log = self.acklink_log
                self.downlink_log = self.datalink_log

            self.mm_link_cmd = [
                'mm-link', self.uplink_trace, self.downlink_trace, '--once',
                '--uplink-log=' + self.uplink_log,
                '--downlink-log=' + self.downlink_log]
            self.remote_ip = '$MAHIMAHI_BASE'
            self.remote_src_file = self.src_file
        else:  # remote setup
            (self.remote_addr, self.remote_dir) = self.remote.split(':')

            self.ssh_cmd = ['ssh']
            if self.private_key:
                self.ssh_cmd += ['-i', self.private_key]
            self.ssh_cmd.append(self.remote_addr)

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
        sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
        sys.stderr.write('Running %s %s...\n' % (self.cc, self.first_to_run))
        proc_first = Popen(cmd, stdout=PIPE, preexec_fn=os.setsid)

        # find port printed
        port = self.get_port(proc_first)

        # sleep just in case the process isn't quite listening yet
        # the cleaner approach might be to try to verify the socket is open
        time.sleep(self.first_to_run_setup_time)

        # run the other side specified by self.second_to_run
        cmd = ' '.join(self.mm_link_cmd)
        cmd += (" -- sh -c 'python %s %s %s %s'" %
                (self.src_file, self.second_to_run, self.remote_ip, port))
        sys.stderr.write('+ ' + cmd + '\n')
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

    # test congestion control using mm-tunnelclient/mm-tunnelserver
    def run_with_tunnel(self):
        # ts: mm-tunnelserver  tc: mm-tunnelclient
        # prepare ingress and egress logs
        self.ts_ilogs = []
        self.ts_elogs = []
        self.tc_ilogs = []
        self.tc_elogs = []

        for i in xrange(self.flows):
            self.ts_ilogs.append('/tmp/ts%s.ingress.log' % (i + 1))
            self.ts_elogs.append('/tmp/ts%s.egress.log' % (i + 1))
            self.tc_ilogs.append('/tmp/tc%s.ingress.log' % (i + 1))
            self.tc_elogs.append('/tmp/tc%s.egress.log' % (i + 1))

        # run mm-tunnelserver manager
        if self.remote:
            ts_manager_cmd = self.ssh_cmd + ['python',
                                             self.remote_tunnel_manager]
        else:
            ts_manager_cmd = ['python', self.tunnel_manager]

        sys.stderr.write('tunnel server manager (tsm) ' +
                         ' '.join(ts_manager_cmd) + '\n')
        ts_manager_proc = Popen(ts_manager_cmd, stdin=PIPE,
                                stdout=PIPE, preexec_fn=os.setsid)

        # run mm-tunnelclient manager
        tc_manager_cmd = ['python', self.tunnel_manager]
        if not self.remote:
            tc_manager_cmd = self.mm_link_cmd + tc_manager_cmd

        sys.stderr.write('tunnel client manager (tcm) ' +
                         ' '.join(tc_manager_cmd) + '\n')
        tc_manager_proc = Popen(tc_manager_cmd, stdin=PIPE,
                                stdout=PIPE, preexec_fn=os.setsid)

        for i in xrange(self.flows):
            tun_id = i + 1
            readline_cmd = 'tunnel %s readline\n' % tun_id

            # run mm-tunnelserver
            ts_cmd = ('mm-tunnelserver --ingress-log=%s --egress-log=%s' %
                      (self.ts_ilogs[i], self.ts_elogs[i]))
            ts_cmd = 'tunnel %s %s\n' % (tun_id, ts_cmd)

            sys.stderr.write('(tsm) ' + ts_cmd)
            ts_manager_proc.stdin.write(ts_cmd)

            # read the command for mm-tunnelclient to run
            sys.stderr.write('(tsm) ' + readline_cmd)
            ts_manager_proc.stdin.write(readline_cmd)

            cmd = ts_manager_proc.stdout.readline().split()
            cmd[1] = self.remote_ip
            tc_private_ip = cmd[3]  # client private IP
            ts_private_ip = cmd[4]  # server private IP

            # run mm-tunnelclient
            tc_cmd = ('%s --ingress-log=%s --egress-log=%s' %
                      (' '.join(cmd), self.tc_ilogs[i], self.tc_elogs[i]))
            tc_cmd = 'tunnel %s %s\n' % (tun_id, tc_cmd)
            sys.stderr.write('(tcm) ' + tc_cmd)
            tc_manager_proc.stdin.write(tc_cmd)

            if self.first_to_run == 'receiver':
                recv_cmd = ('tunnel %s python %s receiver\n' %
                            (tun_id, self.remote_src_file))
                sys.stderr.write('(tsm) ' + recv_cmd)
                ts_manager_proc.stdin.write(recv_cmd)

                # find printed port
                port = None
                while not port:
                    sys.stderr.write('(tsm) ' + readline_cmd)
                    ts_manager_proc.stdin.write(readline_cmd)
                    port = self.get_port(ts_manager_proc)

                send_cmd = ('tunnel %s python %s sender %s %s\n' %
                            (tun_id, self.src_file, ts_private_ip, port))
                sys.stderr.write('(tcm) ' + send_cmd)
                tc_manager_proc.stdin.write(send_cmd)
            else:
                send_cmd = ('tunnel %s python %s sender\n' %
                            (tun_id, self.src_file))
                sys.stderr.write('(tcm) ' + send_cmd)
                tc_manager_proc.stdin.write(send_cmd)

                # find printed port
                port = None
                while not port:
                    sys.stderr.write('(tcm) ' + readline_cmd)
                    tc_manager_proc.stdin.write(readline_cmd)
                    port = self.get_port(tc_manager_proc)

                recv_cmd = (
                    'tunnel %s python %s receiver %s %s\n' %
                    (tun_id, self.remote_src_file, tc_private_ip, port))
                sys.stderr.write('(tsm) ' + recv_cmd)
                ts_manager_proc.stdin.write(recv_cmd)

        time.sleep(self.runtime)

        sys.stderr.write('(tsm) halt\n')
        ts_manager_proc.stdin.write('halt\n')

        sys.stderr.write('(tcm) halt\n')
        tc_manager_proc.stdin.write('halt\n')

        self.merge_tunnel_logs()
        sys.stderr.write('Done\n')

    def merge_tunnel_logs(self):
        tun_datalink_logs = []
        tun_acklink_logs = []

        for i in xrange(self.flows):
            if self.remote:
                # download logs from remote side
                scp_cmd = ['scp']
                if self.private_key:
                    scp_cmd += ['-i', self.private_key]

                check_call(scp_cmd + [self.remote_addr + ':' +
                                      self.ts_ilogs[i], self.ts_ilogs[i]])
                check_call(scp_cmd + [self.remote_addr + ':' +
                                      self.ts_elogs[i], self.ts_elogs[i]])

            tun_datalink_log = '/tmp/tun_datalink%s.log' % (i + 1)
            tun_acklink_log = '/tmp/tun_acklink%s.log' % (i + 1)

            cmd = ['mm-tunnel-merge-logs', 'single', '-i', self.ts_ilogs[i],
                   '-e', self.tc_elogs[i], '-o', tun_datalink_log]
            sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
            check_call(cmd)

            cmd = ['mm-tunnel-merge-logs', 'single', '-i', self.tc_ilogs[i],
                   '-e', self.ts_elogs[i], '-o', tun_acklink_log]
            sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
            check_call(cmd)

            tun_datalink_logs.append(tun_datalink_log)
            tun_acklink_logs.append(tun_acklink_log)

        cmd = ['mm-tunnel-merge-logs', 'multiple', '-o', self.tun_datalink_log]
        if not self.remote:
            cmd += ['--link-log', self.datalink_log]
        cmd += tun_datalink_logs
        sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
        check_call(cmd)

        cmd = ['mm-tunnel-merge-logs', 'multiple', '-o', self.tun_acklink_log]
        if not self.remote:
            cmd += ['--link-log', self.acklink_log]
        cmd += tun_acklink_logs
        sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
        check_call(cmd)

    def run_congestion_control(self):
        self.run_with_tunnel() if self.flows else self.run_without_tunnel()

    def gen_results(self):
        if self.flows:
            datalink_log = self.tun_datalink_log
            acklink_log = self.tun_acklink_log
            throughput_cmd = 'mm-tunnel-throughput'
            delay_cmd = 'mm-tunnel-delay'
        else:
            datalink_log = self.datalink_log
            acklink_log = self.acklink_log
            throughput_cmd = 'mm-throughput-graph'
            delay_cmd = 'mm-delay-graph'

        datalink_throughput_svg = path.join(
            self.test_dir, '%s_datalink_throughput.svg' % self.cc)
        datalink_delay_svg = path.join(
            self.test_dir, '%s_datalink_delay.svg' % self.cc)
        acklink_throughput_svg = path.join(
            self.test_dir, '%s_acklink_throughput.svg' % self.cc)
        acklink_delay_svg = path.join(
            self.test_dir, '%s_acklink_delay.svg' % self.cc)

        stats_log = path.join(self.test_dir, '%s_stats.log' % self.cc)
        stats = open(stats_log, 'w')

        sys.stderr.write('\n')
        # Data link
        sys.stderr.write('* Data link statistics:\n')

        # throughput
        datalink_throughput = open(datalink_throughput_svg, 'w')
        cmd = [throughput_cmd, '500', datalink_log]

        sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
        proc = Popen(cmd, stdout=datalink_throughput, stderr=PIPE)
        datalink_results = proc.communicate()[1]
        sys.stderr.write(datalink_results)
        stats.write(datalink_results)

        datalink_throughput.close()
        self.assertEqual(proc.returncode, 0)

        # delay
        datalink_delay = open(datalink_delay_svg, 'w')
        cmd = [delay_cmd, datalink_log]

        sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
        proc = Popen(cmd, stdout=datalink_delay, stderr=DEVNULL)
        proc.communicate()

        datalink_delay.close()
        self.assertEqual(proc.returncode, 0)

        # ACK link
        sys.stderr.write('* ACK link statistics:\n')

        # throughput
        acklink_throughput = open(acklink_throughput_svg, 'w')
        cmd = [throughput_cmd, '500', acklink_log]

        sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
        proc = Popen(cmd, stdout=acklink_throughput, stderr=PIPE)
        acklink_results = proc.communicate()[1]
        sys.stderr.write(acklink_results)
        stats.write(acklink_results)

        acklink_throughput.close()
        self.assertEqual(proc.returncode, 0)

        # delay
        acklink_delay = open(acklink_delay_svg, 'w')
        cmd = [delay_cmd, acklink_log]

        sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
        proc = Popen(cmd, stdout=acklink_delay, stderr=DEVNULL)
        proc.communicate()

        acklink_delay.close()
        self.assertEqual(proc.returncode, 0)

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
