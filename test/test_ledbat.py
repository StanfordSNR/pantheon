import os, subprocess
import unittest

class TestLedbat(unittest.TestCase):
    def test_diff(self):
        DEVNULL = open(os.devnull, 'wb')
        src_file = '../src/ledbat.py'
        input_file = 'test_files/random_input'
        output_file = 'test_files/ledbat_output'

        # run setup, ignore any output
        setup_cmd = 'python %s setup' % src_file
        setup_proc = subprocess.Popen(setup_cmd, shell = True,
                        stdout = DEVNULL, stderr = DEVNULL)
        setup_proc.communicate()
        
        # find unused port
        port_proc = subprocess.Popen('../src/find_unused_port',
                    stdout = subprocess.PIPE, shell = True) 
        port = port_proc.communicate()[0]

        # run receiver, which outputs to output_file 
        recv_cmd = 'python %s receiver %s' % (src_file, port)
        output_f = open(output_file, 'wb')
        recv_proc = subprocess.Popen(recv_cmd, shell = True,
                    stdout = output_f, stderr = DEVNULL)

        # run sender, which gets input from input_file 
        ip = '127.0.0.1'
        send_cmd = 'python %s sender %s %s' % (src_file, ip, port)
        input_f = open(input_file, 'rb')
        send_proc = subprocess.Popen(send_cmd, shell = True,
                    stdin = input_f, stdout = DEVNULL, stderr = DEVNULL)

        # wait until receiver and sender finish transferring 
        send_proc.communicate()
        recv_proc.communicate()
        output_f.close()
        input_f.close()
        DEVNULL.close()

        # find the difference between the file sent and received
        diff_cmd = 'diff %s %s' % (input_file, output_file) 
        diff_proc = subprocess.Popen(diff_cmd, shell = True,
                    stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        diff_output = diff_proc.communicate()[0]

        # check the difference result
        self.assertEqual(diff_output, '')

if __name__ == '__main__':
    unittest.main()
