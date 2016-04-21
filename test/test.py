import os, sys
from subprocess import Popen, PIPE
import filecmp, tempfile
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

    print "Congestion control option is not valid."
    return None

# generate tmp file of 'size' (MB)
def generate_tmp_file(size):
    f = tempfile.NamedTemporaryFile(delete=False) 
    f.write(os.urandom(1024 * 1024 * size))
    f.close()
    return f.name

class TestCongestionControl(unittest.TestCase):
    # run parameterized test cases
    def __init__(self, test_name, src_file):
        super(TestCongestionControl, self).__init__(test_name)
        self.src_file = src_file

    # congestion control test
    def test_congestion_control(self):
        src_file = self.src_file

        # open /dev/null to ignore some output
        DEVNULL = open(os.devnull, 'wb')

        # generate input file of a random name
        input_fname = generate_tmp_file(1) 
        input_file = open(input_fname, 'rb')

        # open output file of a random name
        output_file = tempfile.NamedTemporaryFile(delete=False)
        output_fname = output_file.name

        # run setup, ignore any output
        setup_cmd = ['python', src_file, 'setup'] 
        setup_proc = Popen(setup_cmd, stdout=DEVNULL, stderr=DEVNULL)
        setup_proc.wait()
        
        # run receiver, which outputs to output_file 
        recv_cmd = ['python', src_file, 'receiver'] 
        recv_proc = Popen(recv_cmd, stdout=output_file, stderr=PIPE)

        # find port that receiver prints
        port_info = recv_proc.stderr.readline()
        port = port_info.rstrip().rsplit(' ', 1)[1]

        # run sender, which gets input from input_file 
        ip = '127.0.0.1'
        send_cmd = ['python', src_file, 'sender', ip, port]
        send_proc = Popen(send_cmd, stdin=input_file, 
                    stdout=DEVNULL, stderr=DEVNULL)

        # wait until the sender and receiver finish transferring 
        send_proc.communicate()
        recv_proc.communicate()

        # close files
        DEVNULL.close()
        input_file.close()
        output_file.close()

        # compare the files sent and received 
        diff = filecmp.cmp(input_fname, output_fname)

        # remove generated files anyway
        os.unlink(input_fname)
        os.unlink(output_fname)

        self.assertTrue(diff)

def main():
    if len(sys.argv) != 2:
        test_usage()
        return

    # find the path of source script of congestion control to run
    cc_option = sys.argv[1]
    src_fname = parse_cc_option(cc_option)
    if src_fname is None:
        return
    src_path = os.path.join(os.path.dirname(__file__), '../src') 
    src_file = os.path.join(src_path, src_fname) 

    # create test suite to run
    suite = unittest.TestSuite()
    suite.addTest(TestCongestionControl("test_congestion_control", src_file))
    unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
   main() 
