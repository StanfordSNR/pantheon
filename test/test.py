#!/usr/bin/python

import os, sys, signal, unittest
from subprocess import Popen, PIPE, check_call, check_output

# print test usage
def usage():
    print 'Usage:'
    print './test.py <congestion-control-name>'
    sys.exit(1)

class TestCongestionControl(unittest.TestCase):
    def timeout_handler(signum, frame):
        raise

    def who_goes_first(self):
        who_goes_first_cmd = 'python %s who_goes_first' % self.src_file
        who_goes_first_info = check_output(who_goes_first_cmd, shell=True)
        self.first_to_run = who_goes_first_info.split(' ')[0].lower()
        self.assertTrue(self.first_to_run == 'receiver' or self.first_to_run == 'sender', msg='Need to specify receiver or sender first')
        sys.stderr.write('Done\n')

    def prepare_mahimahi(self):
        self.ip = '$MAHIMAHI_BASE'
        traces_dir = '/usr/share/mahimahi/traces/'
        self.datalink_log = '%s/%s_datalink.log' % (self.test_dir, self.cc_option)
        self.acklink_log = '%s/%s_acklink.log' % (self.test_dir, self.cc_option)

        if self.first_to_run == 'receiver':
            self.uplink_trace = traces_dir + 'Verizon-LTE-driving.up'
            self.downlink_trace = traces_dir + 'Verizon-LTE-driving.down'
            self.uplink_log = self.datalink_log
            self.downlink_log = self.acklink_log
            self.second_to_run = 'sender'
        else:
            self.uplink_trace = traces_dir + 'Verizon-LTE-driving.down'
            self.downlink_trace = traces_dir + 'Verizon-LTE-driving.up'
            self.uplink_log = self.acklink_log
            self.downlink_log = self.datalink_log
            self.second_to_run = 'receiver'

    def run_congestion_control(self):
        # run the side specified by self.first_to_run
        cmd = 'python %s %s' % (self.src_file, self.first_to_run)
        sys.stderr.write('+ ' + cmd + '\n')
        sys.stderr.write('Running %s %s...\n' % (self.cc_option, self.first_to_run))
        proc1 = Popen(cmd, stdout=DEVNULL, stderr=PIPE, shell=True,
                      preexec_fn=os.setpgrp)

        # find port printed
        port_info = proc1.stderr.readline()
        port = port_info.rstrip().rsplit(' ', 1)[-1]
        self.assertTrue(port.isdigit())

        # run the other side specified by self.second_to_run
        cmd = 'python %s %s %s %s' % (self.src_file, self.second_to_run,
                                      self.ip, port)
        mm_cmd = "mm-link %s %s --once --uplink-log=%s --downlink-log=%s" \
                 " -- sh -c '%s'" % (self.uplink_trace, self.downlink_trace,
                 self.uplink_log, self.downlink_log, cmd)
        sys.stderr.write('+ ' + mm_cmd + '\n')
        sys.stderr.write('Running %s %s...\n' % (self.cc_option, self.second_to_run))
        proc2 = Popen(mm_cmd, stdout=DEVNULL, stderr=PIPE, shell=True,
                      preexec_fn=os.setpgrp)

        # run for 60 seconds
        signal.signal(signal.SIGALRM, self.timeout_handler)
        signal.alarm(60)

        try:
            proc2.communicate()
        except:
            sys.stderr.write('Done\n')
        else:
            sys.stderr.write('Running is shorter than 60s\n')
            sys.exit(1)

        os.killpg(os.getpgid(proc2.pid), signal.SIGTERM)
        os.killpg(os.getpgid(proc1.pid), signal.SIGTERM)

    def gen_results(self):
        datalink_throughput_svg = '%s/%s_datalink_throughput.svg' \
                                   % (self.test_dir, self.cc_option)
        datalink_delay_svg = '%s/%s_datalink_delay.svg' \
                              % (self.test_dir, self.cc_option)
        acklink_throughput_svg = '%s/%s_acklink_throughput.svg' \
                                  % (self.test_dir, self.cc_option)
        acklink_delay_svg = '%s/%s_acklink_delay.svg' \
                             % (self.test_dir, self.cc_option)

        stats_log = '%s/%s_stats.log' % (self.test_dir, self.cc_option)
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
        self.cc_option = sys.argv[1].lower()
        self.test_dir = os.path.abspath(os.path.dirname(__file__))
        src_dir = os.path.abspath(os.path.join(self.test_dir, '../src'))
        self.src_file = os.path.join(src_dir, self.cc_option + '.py')

        # record who goes first
        self.who_goes_first()

        # prepare mahimahi
        self.prepare_mahimahi()

        # run receiver and sender
        self.run_congestion_control()

        # generate results, including statistics and graphs
        self.gen_results()

def main():
    if len(sys.argv) != 2:
        usage()

    # create test suite to run
    suite = unittest.TestSuite()
    suite.addTest(TestCongestionControl('test_congestion_control'))
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)

if __name__ == '__main__':
    DEVNULL = open(os.devnull, 'wb')
    main()
    DEVNULL.close()
