#!/usr/bin/python

import os, sys, signal 
from subprocess import Popen, PIPE
import unittest

# print test usage
def test_usage():
    print "Test Usage:"
    print "./test.py congestion-control-name"
    sys.exit(1)

class TestCongestionControl(unittest.TestCase):
    # run parameterized test cases
    def __init__(self, test_name, cc_option):
        super(TestCongestionControl, self).__init__(test_name)
        self.cc_option = cc_option
        self.DEVNULL = open(os.devnull, 'wb')

    def __del__(self):
        self.DEVNULL.close()

    def timeout_handler(signum, frame):
        raise

    def run_congestion_control(self, first_to_run):
        second_to_run = 'sender'
        if first_to_run == 'sender':
            second_to_run = 'receiver'

        # run the side specified by first_to_run
        cmd1 = ['python', self.src_file, first_to_run] 
        proc1 = Popen(cmd1, stdout=self.DEVNULL, stderr=PIPE)

        # find port printed
        port_info = proc1.stderr.readline()
        port = port_info.rstrip().rsplit(' ', 1)[-1]

        # run the other side specified by second_to_run
        cmd2 = "'python %s %s %s %s'" % (self.src_file, second_to_run, 
                                         self.ip, port)
        mm_cmd = 'mm-link %s %s --once --uplink-log=%s --downlink-log=%s \
                  -- sh -c %s' % (self.uplink_trace, self.downlink_trace,
                  self.uplink_log, self.downlink_log, cmd2) 

        proc2 = Popen(mm_cmd, shell=True, 
                      stdout=self.DEVNULL, stderr=PIPE)

        sys.stderr.write('Running %s...\n' % self.cc_option)

        # running for 60 seconds
        signal.signal(signal.SIGALRM, self.timeout_handler)
        signal.alarm(60)

        try:
            proc2_err = proc2.communicate()[1]
        except:
            sys.stderr.write('Done\n')
        else:
            if proc2.returncode != 0:
                sys.stderr.write(proc2_err)
            else:
                sys.stderr.write('Running is shorter than 60s\n')
            sys.exit(1)

        proc2.kill()
        proc1.kill()

    # congestion control test
    def test_congestion_control(self):
        cc_option = self.cc_option
        test_dir = os.path.abspath(os.path.dirname(__file__))
        src_dir = os.path.abspath(os.path.join(test_dir, '../src')) 
        self.src_file = os.path.join(src_dir, cc_option + '.py') 

        # run setup
        setup_cmd = ['python', self.src_file, 'setup'] 
        setup_proc = Popen(setup_cmd, stdout=self.DEVNULL, stderr=PIPE)
        setup_info = setup_proc.communicate()[1] 
        if setup_proc.returncode != 0:
            sys.stderr.write(setup_info)
            sys.exit(1)

        setup_info = setup_info.rstrip().rsplit('\n', 1)[-1]
        first_to_run = setup_info.split(' ')[0].lower()
        if first_to_run != 'receiver' and first_to_run != 'sender':
            sys.stderr.write('Requires specifying receiver or sender first')
            sys.exit(1)
        
        # prepare mahimahi
        traces_dir = '/usr/share/mahimahi/traces/' 
        self.datalink_log = os.path.join(test_dir, '%s_datalink.log' % cc_option) 
        self.acklink_log = os.path.join(test_dir, '%s_acklink.log' % cc_option) 

        if first_to_run == 'receiver':
            self.uplink_trace = traces_dir + 'Verizon-LTE-driving.up'
            self.downlink_trace = traces_dir + 'Verizon-LTE-driving.down'
            self.uplink_log = self.datalink_log
            self.downlink_log = self.acklink_log
        else:
            self.uplink_trace = traces_dir + 'Verizon-LTE-driving.down'
            self.downlink_trace = traces_dir + 'Verizon-LTE-driving.up'
            self.uplink_log = self.acklink_log
            self.downlink_log = self.datalink_log

        self.ip = '$MAHIMAHI_BASE'

        # run receiver and sender depending on the run order
        self.run_congestion_control(first_to_run)

        # generate throughput graphs
        sys.stderr.write('* Data link statistics:\n')
        datalink_throughput = open(os.path.join(test_dir, 
                                '%s_datalink_throughput.html' % cc_option), 'wb')
        proc = Popen(['mm-throughput-graph', '500', self.datalink_log],
                     stdout=datalink_throughput, stderr=PIPE)
        datalink_results = proc.communicate()[1]
        sys.stderr.write(datalink_results)
        datalink_throughput.close()

        sys.stderr.write('* ACK link statistics:\n')
        acklink_throughput = open(os.path.join(test_dir, 
                                '%s_acklink_throughput.html' % cc_option), 'wb')
        proc = Popen(['mm-throughput-graph', '500', self.acklink_log],
                     stdout=acklink_throughput, stderr=PIPE)
        acklink_results = proc.communicate()[1]
        sys.stderr.write(acklink_results)
        acklink_throughput.close()

def main():
    if len(sys.argv) != 2:
        test_usage()

    cc_option = sys.argv[1]

    # create test suite to run
    suite = unittest.TestSuite()
    suite.addTest(TestCongestionControl("test_congestion_control", cc_option))
    success = unittest.TextTestRunner().run(suite).wasSuccessful()
    if not success:
        sys.exit(1)

if __name__ == '__main__':
   main() 
