import os, subprocess
import unittest

class TestLedbat(unittest.TestCase):

    def test_diff(self):
        DEVNULL = open(os.devnull, 'wb')
        ledbat_src = '../src/ledbat.py'
        input_file = 'test_files/random_input'
        output_file = 'test_files/ledbat_output'

        # run ledbat setup, ignore any output
        setup_cmd = 'python %s setup' % ledbat_src
        setup_proc = subprocess.Popen(setup_cmd, shell = True,
                        stdout = DEVNULL, stderr = DEVNULL)
        setup_proc.communicate()
        
        # find unused port
        port_proc = subprocess.Popen('../src/find_unused_port',
                    stdout = subprocess.PIPE, shell = True) 
        port = port_proc.communicate()[0]

        # run ledbat receiver, which outputs to a file: ledbat-output
        recv_cmd = 'python %s receiver %s' % (ledbat_src, port)
        ledbat_output = open(output_file, 'wb')
        recv_proc = subprocess.Popen(recv_cmd, shell = True,
                    stdout = ledbat_output, stderr = DEVNULL)

        # run ledbat sender, which gets input from random-input 
        ip = '127.0.0.1'
        send_cmd = 'python %s sender %s %s' % (ledbat_src, ip, port)
        ledbat_input = open(input_file, 'rb')
        send_proc = subprocess.Popen(send_cmd, shell = True,
                    stdin = ledbat_input, stdout = DEVNULL, stderr = DEVNULL)

        # wait until receiver and sender finish transferring 
        send_proc.communicate()
        recv_proc.communicate()
        ledbat_output.close()
        ledbat_input.close()
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
