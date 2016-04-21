import os, sys
from subprocess import Popen, PIPE
from interruptingcow import timeout
import unittest

# print test usage
def test_usage():
    print "Test Usage:"
    print "python test.py scheme"

# parse congestion control option, return the name of script to run if valid
def parse_cc_option(cc_option):
    cc_option = cc_option.lower()

    # add more congestion control options here
    if cc_option == 'ledbat':
        return 'ledbat.py'
    if cc_option == 'default_tcp':
        return 'default_tcp.py'

    print "Congestion control option is not valid."
    return None

class TestCongestionControl(unittest.TestCase):
    # run parameterized test cases
    def __init__(self, test_name, src_fname):
        super(TestCongestionControl, self).__init__(test_name)
        self.src_fname = src_fname

    # congestion control test
    def test_congestion_control(self):
        src_fname = self.src_fname
        src_path = os.path.join(os.path.dirname(__file__), '../src') 
        src_file = os.path.join(src_path, src_fname) 

        # open /dev/null to ignore some output
        DEVNULL = open(os.devnull, 'wb')

        # run setup, ignore any output
        setup_cmd = ['python', src_file, 'setup'] 
        setup_proc = Popen(setup_cmd, stdout=DEVNULL, stderr=DEVNULL)
        setup_proc.communicate()
        
        # run receiver, which outputs to output_file 
        recv_cmd = ['python', src_file, 'receiver'] 
        recv_proc = Popen(recv_cmd, stdout=DEVNULL, stderr=PIPE)

        # find port that receiver prints
        port_info = recv_proc.stderr.readline()
        port = port_info.rstrip().rsplit(' ', 1)[1]

        # run sender, which gets input from input_file 
        ip = '127.0.0.1'
        send_cmd = ['python', src_file, 'sender', ip, port]

        success = False
        if src_fname == 'default_tcp.py':
            send_proc = Popen(send_cmd, stdout=DEVNULL, stderr=DEVNULL)
            send_proc.communicate()
            recv_proc.terminate()
            success = True 
        else:
            send_proc = Popen(send_cmd, stdin=PIPE, 
                        stdout=DEVNULL, stderr=DEVNULL)
            # write random stuff to sender for 10 seconds
            try:
                with timeout(10, exception=RuntimeError):
                    while True:
                        send_proc.stdin.write(os.urandom(1024 * 128))
            except:
                success = True

            send_proc.stdin.close()
            send_proc.terminate()
            recv_proc.terminate()

        # close files
        DEVNULL.close()

        self.assertTrue(success)

def main():
    if len(sys.argv) != 2:
        test_usage()
        return

    # find the path of source script of congestion control to run
    cc_option = sys.argv[1]
    src_fname = parse_cc_option(cc_option)
    if src_fname is None:
        return

    # create test suite to run
    suite = unittest.TestSuite()
    suite.addTest(TestCongestionControl("test_congestion_control", src_fname))
    unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
   main() 
