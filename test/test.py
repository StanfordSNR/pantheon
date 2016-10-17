#!/usr/bin/python

import os
import sys
import unittest
import time
import signal
import argparse
from os import path
from subprocess import Popen, PIPE, check_call, check_output


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('cc', metavar='congestion-control', type=str,
                        help='name of a congestion control scheme')
    parser.add_argument('-f', action='store', dest='flows', type=int,
                        default=1, help='number of flows '
                        '(mm-tunnelclient/mm-tunnelserver pairs)')
    parser.add_argument('-r', action='store', dest='remote_addr', type=str,
                        help='remote address: [user@]hostname')
    parser.add_argument('-i', action='store', dest='private_key', type=str,
                        help='identity file (private key) for ssh/scp to use')

    return parser.parse_args()

class TestCongestionControl(unittest.TestCase):
    def __init__(self, test_name, args):
        super(TestCongestionControl, self).__init__(test_name)
        self.cc = args.cc.lower()
        self.flows = args.flows
        self.remote_addr = args.remote_addr
        self.private_key = args.private_key

    def timeout_handler(signum, frame):
        raise

    def who_goes_first(self):
        who_goes_first_cmd = ['python', self.src_file, 'who_goes_first']
        who_goes_first_info = check_output(who_goes_first_cmd)
        self.first_to_run = who_goes_first_info.split(' ')[0].lower()
        self.assertTrue(
            self.first_to_run == 'receiver' or self.first_to_run == 'sender',
            msg='Need to specify receiver or sender first')
        self.second_to_run = ('sender' if self.first_to_run == 'receiver'
                              else 'receiver')
        sys.stderr.write('Done\n')

    def setup(self):
        self.test_runtime = 60
        self.first_to_run_setup_time = 1
        self.datalink_log = path.join(self.test_dir, self.cc + '_datalink.log')
        self.acklink_log = path.join(self.test_dir, self.cc + '_acklink.log')

        if self.flows > 0:
            self.flows_datalink_log = path.join(self.test_dir, self.cc +
                                                '_flows_datalink.log')
            self.flows_acklink_log = path.join(self.test_dir, self.cc +
                                               '_flows_acklink.log')

        if self.remote_addr is None: # local setup
            self.ip = '$MAHIMAHI_BASE'
            traces_dir = '/usr/share/mahimahi/traces/'
            if self.first_to_run == 'receiver' or self.flows > 0:
                self.uplink_trace = traces_dir + 'Verizon-LTE-short.up'
                self.downlink_trace = traces_dir + 'Verizon-LTE-short.down'
                self.uplink_log = self.datalink_log
                self.downlink_log = self.acklink_log
            else:
                self.uplink_trace = traces_dir + 'Verizon-LTE-short.down'
                self.downlink_trace = traces_dir + 'Verizon-LTE-short.up'
                self.uplink_log = self.acklink_log
                self.downlink_log = self.datalink_log
        else: # remote setup
            self.ssh_cmd = ['ssh', self.remote_addr]
            if self.private_key is not None:
                self.ssh_cmd += ['-i', self.private_key]
            self.remote_ip = self.remote_addr.split('@')[-1]

    # test congestion control without running mm-tunnelclient/mm-tunnelserver
    def run_without_tunnel(self):
        # run the side specified by self.first_to_run
        cmd = ['python', self.src_file, self.first_to_run]
        sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
        sys.stderr.write('Running %s %s...\n' % (self.cc, self.first_to_run))
        proc_first = Popen(cmd, stdout=PIPE, preexec_fn=os.setsid)

        # find port printed
        port_info = proc_first.stdout.readline()
        port = port_info.rstrip().rsplit(' ', 1)[-1]
        self.assertTrue(port.isdigit())

        # sleep just in case the process isn't quite listening yet
        # the cleaner approach might be to try to verify the socket is open
        time.sleep(self.first_to_run_setup_time)

        # run the other side specified by self.second_to_run
        cmd = ('mm-link %s %s --once --uplink-log=%s --downlink-log=%s' %
               (self.uplink_trace, self.downlink_trace,
                self.uplink_log, self.downlink_log))
        cmd += (" -- sh -c 'python %s %s %s %s'" %
                (self.src_file, self.second_to_run, self.ip, port))
        sys.stderr.write('+ ' + cmd + '\n')
        sys.stderr.write('Running %s %s...\n' % (self.cc, self.second_to_run))
        proc_second = Popen(cmd, stdout=PIPE, shell=True, preexec_fn=os.setsid)

        signal.signal(signal.SIGALRM, self.timeout_handler)
        signal.alarm(self.test_runtime)

        try:
            proc_second.communicate()
        except:
            sys.stderr.write('Done\n')
        else:
            self.fail('Test exited before time limit')
        finally:
            os.killpg(os.getpgid(proc_first.pid), signal.SIGKILL)
            os.killpg(os.getpgid(proc_second.pid), signal.SIGKILL)

    def run_congestion_control(self):
        self.run_with_tunnel() if self.flows > 0 else self.run_without_tunnel()

    def run_multiple_flows(self):
        tunserver_ilogs = []
        tunserver_elogs = []
        tunclient_ilogs = []
        tunclient_elogs = []

        tunserver_procs = []
        tunclient_cmds = '{ '

        for i in xrange(self.flows):
            tunserver_ilogs.append('/tmp/tunserver%i.ingress.log' % (i + 1))
            tunserver_elogs.append('/tmp/tunserver%i.egress.log' % (i + 1))
            tunclient_ilogs.append('/tmp/tunclient%i.ingress.log' % (i + 1))
            tunclient_elogs.append('/tmp/tunclient%i.egress.log' % (i + 1))

            # start mm-tunnelserver
            tunserver_cmd = ['mm-tunnelserver',
                             '--ingress-log=' + tunserver_ilogs[i],
                             '--egress-log=' + tunserver_elogs[i]]
            sys.stderr.write('+ ' + ' '.join(tunserver_cmd) + '\n')
            tunserver_proc = Popen(tunserver_cmd, stdin=PIPE, stdout=PIPE,
                                   preexec_fn=os.setsid)
            tunserver_procs.append(tunserver_proc)

            # prepare cmds for mm-tunnelclient
            tunclient_cmd = tunserver_proc.stdout.readline().split()
            tunclient_cmd[1] = self.ip
            tunclient_ip = tunclient_cmd[3]
            tunserver_ip = tunclient_cmd[4]
            tunclient_cmd = ' '.join(tunclient_cmd)
            tunclient_cmd += ' --ingress-log=%s --egress-log=%s ' % \
                             (tunclient_ilogs[i], tunclient_elogs[i])

            if self.first_to_run == 'receiver':
                receiver_cmd = 'python %s receiver\n' % self.src_file
                sys.stderr.write('Flow %i: ' % (i + 1) + receiver_cmd)
                tunserver_proc.stdin.write(receiver_cmd)

                # find port printed
                port_info = tunserver_proc.stdout.readline()
                port = port_info.rstrip().rsplit(' ', 1)[-1]
                self.assertTrue(port.isdigit())

                tunclient_cmd += 'python %s sender %s %s' % (self.src_file,
                                 tunserver_ip, port)

                if i < self.flows - 1:
                    tunclient_cmds += tunclient_cmd + '; } & { sleep %i; ' % \
                                      (self.test_runtime / self.flows)
                else:
                    tunclient_cmds += tunclient_cmd + '; } & wait'
            else:
                tunclient_cmd += 'python %s sender' % self.src_file

                if i < self.flows - 1:
                    tunclient_cmds += tunclient_cmd + '; } & { '
                else:
                    tunclient_cmds += tunclient_cmd + '; } & wait'

        mm_cmd = "mm-link %s %s --once --uplink-log=%s --downlink-log=%s " \
                 "-- sh -c '%s'" % (self.uplink_trace, self.downlink_trace,
                 self.uplink_log, self.downlink_log, tunclient_cmds)
        sys.stderr.write('+ ' + mm_cmd + '\n')

        # sleep just in case the process isn't quite listening yet
        time.sleep(self.first_to_run_setup_time)

        if self.first_to_run == 'receiver':
            tunclient_proc = Popen(mm_cmd, shell=True, preexec_fn=os.setsid)
        else:
            tunclient_proc = Popen(mm_cmd, stdout=PIPE, shell=True,
                                   preexec_fn=os.setsid)
            for i in xrange(self.flows):
                # find port printed
                port_info = tunclient_proc.stdout.readline()
                port = port_info.rstrip().rsplit(' ', 1)[-1]
                self.assertTrue(port.isdigit())

                receiver_cmd = 'python %s receiver %s %s\n' % (self.src_file,
                               tunclient_ip, port)
                sys.stderr.write('Flow %i: ' % (i + 1) + receiver_cmd)
                tunserver_proc.stdin.write(receiver_cmd)

                if i < self.flows - 1:
                    time.sleep(self.test_runtime / self.flows)

        signal.signal(signal.SIGALRM, self.timeout_handler)
        signal.alarm(self.test_runtime)

        try:
            tunclient_proc.communicate()
        except:
            sys.stderr.write('Done\n')
            os.killpg(os.getpgid(tunclient_proc.pid), signal.SIGKILL)
            for i in xrange(self.flows):
                os.killpg(os.getpgid(tunserver_procs[i].pid), signal.SIGKILL)
        else:
            sys.stderr.write('Test exited before test time limit\n')
            os.killpg(os.getpgid(tunclient_proc.pid), signal.SIGKILL)
            for i in xrange(self.flows):
                os.killpg(os.getpgid(tunserver_procs[i].pid), signal.SIGKILL)
            sys.exit(1)

        combine_datalink_cmd = 'mm-combine-multi-flow-logs --link-log=' + \
                               self.uplink_log
        combine_acklink_cmd = 'mm-combine-multi-flow-logs --link-log=' + \
                               self.downlink_log

        for i in xrange(self.flows):
            tun_datalink_log = '/tmp/tun_datalink%s.log' % (i + 1)
            tun_acklink_log = '/tmp/tun_acklink%s.log' % (i + 1)

            combine_tun_logs_cmd = 'mm-combine-tunnel-logs %s %s > %s' % \
                                   (tunserver_ilogs[i], tunclient_elogs[i],
                                    tun_datalink_log)
            sys.stderr.write(combine_tun_logs_cmd + '\n')
            check_call(combine_tun_logs_cmd, shell=True)

            combine_tun_logs_cmd = 'mm-combine-tunnel-logs %s %s > %s' % \
                                   (tunclient_ilogs[i], tunserver_elogs[i],
                                    tun_acklink_log)
            sys.stderr.write(combine_tun_logs_cmd + '\n')
            check_call(combine_tun_logs_cmd, shell=True)

            combine_datalink_cmd += ' ' + tun_datalink_log
            combine_acklink_cmd += ' ' + tun_acklink_log

        combine_datalink_cmd += ' > ' + self.flows_datalink_log
        combine_acklink_cmd += ' > ' + self.flows_acklink_log
        sys.stderr.write(combine_datalink_cmd + '\n')
        sys.stderr.write(combine_acklink_cmd + '\n')
        check_call(combine_datalink_cmd, shell=True)
        check_call(combine_acklink_cmd, shell=True)

    def gen_results(self, flows_str = ''):
        datalink_throughput_svg = path.join(self.test_dir,
            '%s_%sdatalink_throughput.svg' % (self.cc, flows_str))
        datalink_delay_svg = path.join(self.test_dir,
            '%s_%sdatalink_delay.svg' % (self.cc, flows_str))
        acklink_throughput_svg = path.join(self.test_dir,
            '%s_%sacklink_throughput.svg' % (self.cc, flows_str))
        acklink_delay_svg = path.join(self.test_dir,
            '%s_%sacklink_delay.svg' % (self.cc, flows_str))

        stats_log = path.join(self.test_dir,
                              '%s_%sstats.log' % (self.cc, flows_str))
        stats = open(stats_log, 'wb')

        sys.stderr.write('\n')
        delay_cmd = 'mm-signal-delay-graph' if flows_str else 'mm-delay-graph'

        # Data link
        sys.stderr.write('* Data link statistics:\n')
        datalink_throughput = open(datalink_throughput_svg, 'wb')
        proc = Popen(['mm-throughput-graph', '500', self.datalink_log],
                     stdout=datalink_throughput, stderr=PIPE)
        datalink_results = proc.communicate()[1]
        sys.stderr.write(datalink_results)
        stats.write(datalink_results)
        datalink_throughput.close()
        self.assertEqual(proc.returncode, 0)

        datalink_delay = open(datalink_delay_svg, 'wb')

        proc = Popen([delay_cmd, self.datalink_log],
                     stdout=datalink_delay, stderr=DEVNULL)
        proc.communicate()
        datalink_delay.close()
        self.assertEqual(proc.returncode, 0)

        # ACK link
        sys.stderr.write('* ACK link statistics:\n')
        acklink_throughput = open(acklink_throughput_svg, 'wb')
        proc = Popen(['mm-throughput-graph', '500', self.acklink_log],
                      stdout=acklink_throughput, stderr=PIPE)
        acklink_results = proc.communicate()[1]
        sys.stderr.write(acklink_results)
        stats.write(acklink_results)
        acklink_throughput.close()
        self.assertEqual(proc.returncode, 0)

        acklink_delay = open(acklink_delay_svg, 'wb')
        proc = Popen([delay_cmd, self.acklink_log],
                     stdout=acklink_delay, stderr=DEVNULL)
        proc.communicate()
        acklink_delay.close()
        self.assertEqual(proc.returncode, 0)

        stats.close()

    # congestion control test
    def test_congestion_control(self):
        self.test_dir = path.abspath(path.dirname(__file__))
        src_dir = path.abspath(path.join(self.test_dir, '../src'))
        self.src_file = path.join(src_dir, self.cc + '.py')

        # record who goes first
        self.who_goes_first()

        # local or remote setup before running tests
        self.setup()

        if self.flows == 0:
            # run receiver and sender
            self.run_congestion_control()
        else:
            # run multiple flows
            self.run_multiple_flows()

        # generate results, including statistics and graphs
        self.gen_results()

        if self.flows > 0:
            self.datalink_log = self.flows_datalink_log
            self.acklink_log = self.flows_acklink_log
            self.gen_results("flows_")


def main():
    args = parse_arguments()

    # create test suite to run
    suite = unittest.TestSuite()
    suite.addTest(TestCongestionControl('test_congestion_control', args))
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)


if __name__ == '__main__':
    DEVNULL = open(os.devnull, 'wb')
    main()
    DEVNULL.close()
