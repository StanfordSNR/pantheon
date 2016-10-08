#!/usr/bin/python

import os
import sys
import unittest
import time
import signal
import argparse
from subprocess import Popen, PIPE, check_call, check_output


class TestCongestionControl(unittest.TestCase):
    def __init__(self, test_name, args):
        super(TestCongestionControl, self).__init__(test_name)
        self.cc_option = args.cc_option.lower()
        self.flows = args.flows

    def timeout_handler(signum, frame):
        raise

    def who_goes_first(self):
        who_goes_first_cmd = 'python %s who_goes_first' % self.src_file
        who_goes_first_info = check_output(who_goes_first_cmd, shell=True)
        self.first_to_run = who_goes_first_info.split(' ')[0].lower()
        self.assertTrue(
            self.first_to_run == 'receiver' or self.first_to_run == 'sender',
            msg='Need to specify receiver or sender first')
        sys.stderr.write('Done\n')

    def prepare_mahimahi(self):
        self.test_runtime = 60
        self.first_to_run_setup_time = 1
        self.ip = '$MAHIMAHI_BASE'

        traces_dir = '/usr/share/mahimahi/traces/'
        self.datalink_log = os.path.join(self.test_dir,
                                         '%s_datalink.log' % self.cc_option)
        self.acklink_log = os.path.join(self.test_dir,
                                        '%s_acklink.log' % self.cc_option)

        if self.first_to_run == 'receiver':
            self.second_to_run = 'sender'
        else:
            self.second_to_run = 'receiver'

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

        # if run multiple flows
        if self.flows > 0:
            self.tunnel_uplogs = []
            self.tunnel_downlogs = []
            for i in xrange(self.flows):
                self.tunnel_uplogs.append(os.path.join(self.test_dir,
                    '%s_tunnel_up%i.log' % (self.cc_option, i + 1)))
                self.tunnel_downlogs.append(os.path.join(self.test_dir,
                    '%s_tunnel_down%i.log' % (self.cc_option, i + 1)))

    def run_congestion_control(self):
        # run the side specified by self.first_to_run
        cmd = 'python %s %s' % (self.src_file, self.first_to_run)
        sys.stderr.write('+ ' + cmd + '\n')
        sys.stderr.write('Running %s %s...\n' %
                         (self.cc_option, self.first_to_run))
        proc1 = Popen(cmd, stdout=PIPE, shell=True, preexec_fn=os.setsid)

        # find port printed
        port_info = proc1.stdout.readline()
        port = port_info.rstrip().rsplit(' ', 1)[-1]
        self.assertTrue(port.isdigit())

        # sleep just in case the process isn't quite listening yet
        time.sleep(self.first_to_run_setup_time)
        # XXX the cleaner approach might be to try to verify the socket is open

        # run the other side specified by self.second_to_run
        cmd = 'python %s %s %s %s' % (self.src_file, self.second_to_run,
                                      self.ip, port)
        mm_cmd = "mm-link %s %s --once --uplink-log=%s --downlink-log=%s " \
                 "-- sh -c '%s'" % (self.uplink_trace, self.downlink_trace,
                 self.uplink_log, self.downlink_log, cmd)
        sys.stderr.write('+ ' + mm_cmd + '\n')
        sys.stderr.write('Running %s %s...\n' %
                         (self.cc_option, self.second_to_run))
        proc2 = Popen(mm_cmd, stdout=PIPE, shell=True, preexec_fn=os.setsid)

        signal.signal(signal.SIGALRM, self.timeout_handler)
        signal.alarm(self.test_runtime)

        try:
            if self.first_to_run == 'receiver':
                proc2.communicate()
            else:
                proc1.communicate()
        except:
            sys.stderr.write('Done\n')
            os.killpg(os.getpgid(proc2.pid), signal.SIGKILL)
            os.killpg(os.getpgid(proc1.pid), signal.SIGKILL)
        else:
            sys.stderr.write('Sender exited before test time limit\n')
            os.killpg(os.getpgid(proc2.pid), signal.SIGKILL)
            os.killpg(os.getpgid(proc1.pid), signal.SIGKILL)
            sys.exit(1)

    def run_multiple_flows(self):
        tunserver_ilogs = []
        tunserver_elogs = []
        tunclient_ilogs = []
        tunclient_elogs = []
        tunserver_procs = []
        tunclient_cmd = '{ '

        for i in xrange(self.flows):
            tunserver_ilogs.append('/tmp/tunserver%i.ingress.log' % (i + 1))
            tunserver_elogs.append('/tmp/tunserver%i.egress.log' % (i + 1))
            tunclient_ilogs.append('/tmp/tunclient%i.ingress.log' % (i + 1))
            tunclient_elogs.append('/tmp/tunclient%i.egress.log' % (i + 1))

            # mm-tunnelserver cmd
            cmd = 'mm-tunnelserver --ingress-log=%s --egress-log=%s ' \
                  'python %s receiver' % (tunserver_ilogs[i],
                  tunserver_elogs[i], self.src_file)

            sys.stderr.write('+ ' + cmd + '\n')
            sys.stderr.write('Flow %i running %s %s...\n' %
                (i + 1, self.cc_option, self.first_to_run))
            proc = Popen(cmd, stdout=PIPE, shell=True, preexec_fn=os.setsid)
            tunserver_procs.append(proc)

            # mm-tunnelclient cmd
            cmd = proc.stdout.readline().split()
            cmd[1] = self.ip
            tunserver_ip = cmd[4]
            cmd = ' '.join(cmd)

            # find port printed
            port_info = proc.stdout.readline()
            port = port_info.rstrip().rsplit(' ', 1)[-1]
            self.assertTrue(port.isdigit())

            # sleep just in case the process isn't quite listening yet
            time.sleep(self.first_to_run_setup_time)

            tunclient_cmd += cmd + ' --ingress-log=%s --egress-log=%s ' \
                'python %s sender %s %s' % (tunclient_ilogs[i],
                 tunclient_elogs[i], self.src_file, tunserver_ip, port)
            if i < self.flows - 1:
                tunclient_cmd += '; } & { sleep %i; ' % \
                                 (self.test_runtime / self.flows)
            else:
                tunclient_cmd += '; } & wait'

        mm_cmd = "mm-link %s %s --once --uplink-log=%s --downlink-log=%s " \
                 "-- sh -c '%s'" % (self.uplink_trace, self.downlink_trace,
                  self.uplink_log, self.downlink_log, tunclient_cmd)

        sys.stderr.write('+ ' + mm_cmd + '\n')
        proc = Popen(mm_cmd, stdout=PIPE, shell=True, preexec_fn=os.setsid)

        signal.signal(signal.SIGALRM, self.timeout_handler)
        signal.alarm(self.test_runtime)

        try:
            proc.communicate()
        except:
            sys.stderr.write('Done\n')
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            for i in xrange(self.flows):
                os.killpg(os.getpgid(tunserver_procs[i].pid), signal.SIGKILL)
        else:
            sys.stderr.write('Test exited before test time limit\n')
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            for i in xrange(self.flows):
                os.killpg(os.getpgid(tunserver_procs[i].pid), signal.SIGKILL)
            sys.exit(1)

    def gen_results(self):
        datalink_throughput_svg = os.path.join(self.test_dir,
                                  '%s_datalink_throughput.svg' % self.cc_option)
        datalink_delay_svg = os.path.join(self.test_dir,
                             '%s_datalink_delay.svg' % self.cc_option)
        acklink_throughput_svg = os.path.join(self.test_dir,
                                 '%s_acklink_throughput.svg' % self.cc_option)
        acklink_delay_svg = os.path.join(self.test_dir,
                            '%s_acklink_delay.svg' % self.cc_option)

        stats_log = os.path.join(self.test_dir, '%s_stats.log' % self.cc_option)
        stats = open(stats_log, 'wb')

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
        proc = Popen(['mm-delay-graph', self.datalink_log],
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
        proc = Popen(['mm-delay-graph', self.acklink_log],
                     stdout=acklink_delay, stderr=DEVNULL)
        proc.communicate()
        acklink_delay.close()
        self.assertEqual(proc.returncode, 0)

        stats.close()

    # congestion control test
    def test_congestion_control(self):
        self.test_dir = os.path.abspath(os.path.dirname(__file__))
        src_dir = os.path.abspath(os.path.join(self.test_dir, '../src'))
        self.src_file = os.path.join(src_dir, self.cc_option + '.py')

        # record who goes first
        self.who_goes_first()

        # prepare mahimahi
        self.prepare_mahimahi()

        if self.flows == 0:
            # run receiver and sender
            self.run_congestion_control()
        else:
            # run multiple flows
            self.run_multiple_flows()

        # generate results, including statistics and graphs
        self.gen_results()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cc_option', metavar='congestion-control', type=str,
                        help='name of a congestion control scheme')
    parser.add_argument('-f', action='store', dest='flows', type=int, default=0,
                        help='number of flows')
    args = parser.parse_args()

    # create test suite to run
    suite = unittest.TestSuite()
    suite.addTest(TestCongestionControl('test_congestion_control', args))
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)


if __name__ == '__main__':
    DEVNULL = open(os.devnull, 'wb')
    main()
    DEVNULL.close()
