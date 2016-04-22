import os, sys, tempfile, subprocess
from subprocess import Popen, PIPE
from interruptingcow import timeout
import unittest

# print test usage
def test_usage():
    print "Test Usage:"
    print "python test.py scheme"

# parse congestion control option, return friendly name and script to run
def parse_cc_option(cc_option):
    # add more congestion control options here
    if cc_option == 'ledbat':
        return 'LEDBAT', 'ledbat.py'

    if cc_option == 'default_tcp':
        return 'Default TCP', 'default_tcp.py'

    print "Congestion control option is not valid."
    return None, None

class TestCongestionControl(unittest.TestCase):
    # run parameterized test cases
    def __init__(self, test_name, cc_option):
        cc_friendly_name, src_name = parse_cc_option(cc_option)

        self.assertTrue(cc_friendly_name is not None)
        self.assertTrue(src_name is not None)

        super(TestCongestionControl, self).__init__(test_name)
        self.cc_friendly_name = cc_friendly_name
        self.src_name = src_name

    # congestion control test
    def test_congestion_control(self):
        cc_friendly_name = self.cc_friendly_name
        src_name = self.src_name
        cc_name = src_name[:-3]
        test_dir = os.path.dirname(__file__)
        src_dir = os.path.join(test_dir, '../src') 
        src_file = os.path.join(src_dir, src_name) 

        # open /dev/null to ignore some output
        DEVNULL = open(os.devnull, 'wb')

        # run setup, ignore any output
        setup_cmd = ['python', src_file, 'setup'] 
        setup_proc = Popen(setup_cmd, stdout=DEVNULL, stderr=DEVNULL)
        setup_proc.communicate()
        
        # run receiver
        recv_cmd = ['python', src_file, 'receiver'] 
        recv_proc = Popen(recv_cmd, stdout=DEVNULL, stderr=PIPE)

        # find port that receiver prints
        port_info = recv_proc.stderr.readline()
        port = port_info.rstrip().rsplit(' ', 1)[1]

        # run sender in mahimahi
        traces_dir = '/usr/share/mahimahi/traces/'
        uplink_trace = traces_dir + 'Verizon-LTE-short.up'
        downlink_trace = traces_dir + 'Verizon-LTE-short.down'
        uplink_log = os.path.join(test_dir, '%s_uplink.log' % cc_name) 
        
        ip = '$MAHIMAHI_BASE'
        send_cmd = "'python %s sender %s %s'" % (src_file, ip, port)
        mahimahi_cmd = 'mm-link %s %s --once --uplink-log=%s -- sh -c %s' % \
                        (uplink_trace, downlink_trace, uplink_log, send_cmd) 

        print 'Running %s...' % cc_friendly_name 
        if src_name == 'default_tcp.py':
            # default_tcp.py runs for 10 seconds itself
            send_proc = Popen(mahimahi_cmd, shell=True, 
                        stdout=DEVNULL, stderr=DEVNULL)
            send_proc.communicate()
            recv_proc.terminate()
        else:
            send_proc = Popen(mahimahi_cmd, shell=True, 
                        stdin=PIPE, stdout=DEVNULL, stderr=DEVNULL)
            # other schemes require writing random data to sender for 10 seconds
            try:
                with timeout(10, exception=RuntimeError):
                    while True:
                        send_proc.stdin.write(os.urandom(1024 * 128))
            except:
                pass
            else:
                print 'Warning: quit earlier!'

            send_proc.stdin.close()
            send_proc.terminate()
            recv_proc.terminate()

        # generate throughput graph
        throughput_graph_file = open(os.path.join(test_dir, 
                                '%s_throughput.html' % cc_name), 'wb')
        subprocess.call(['mm-throughput-graph', '500', uplink_log],
                        stdout=throughput_graph_file)

        # close / remove files
        DEVNULL.close()
        throughput_graph_file.close()

def main():
    if len(sys.argv) != 2:
        test_usage()
        return
    cc_option = sys.argv[1].lower()

    # create test suite to run
    suite = unittest.TestSuite()
    suite.addTest(TestCongestionControl("test_congestion_control", cc_option))
    unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
   main() 
