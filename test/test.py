import os, subprocess
import filecmp, tempfile
import unittest

# generate tmp file of 'size' (MB)
def generate_tmp_file(size):
    f = tempfile.NamedTemporaryFile(delete=False) 
    f.write(os.urandom(1024 * 1024 * size))
    f.close()
        
    return f.name

class TestLedbat(unittest.TestCase):
    def test_diff(self):
        DEVNULL = open(os.devnull, 'wb')
        src_file = '../src/ledbat.py'

        # generate 1MB input file of random name
        input_fname = generate_tmp_file(1) 
        input_file = open(input_fname, 'rb')

        # open output file of random name
        output_file = tempfile.NamedTemporaryFile(delete=False)
        output_fname = output_file.name

        # run setup, ignore any output
        setup_cmd = 'python %s setup' % src_file
        setup_proc = subprocess.Popen(setup_cmd, shell=True,
                        stdout=DEVNULL, stderr=DEVNULL)
        setup_proc.communicate()
        
        # run receiver, which outputs to output_file 
        recv_cmd = 'python %s receiver' % src_file
        recv_proc = subprocess.Popen(recv_cmd, shell=True,
                    stdout=output_file, stderr=subprocess.PIPE)
        port_info = recv_proc.stderr.readline()
        port = port_info.rsplit(' ', 1)[1]

        # run sender, which gets input from input_file 
        ip = '127.0.0.1'
        send_cmd = 'python %s sender %s %s' % (src_file, ip, port)
        send_proc = subprocess.Popen(send_cmd, shell=True,
                    stdin=input_file, stdout=DEVNULL, stderr=DEVNULL)

        # wait until receiver and sender finish transferring 
        send_proc.communicate()
        recv_proc.communicate()

        # close files
        DEVNULL.close()
        input_file.close()
        output_file.close()

        # compare the file sent and received 
        diff = filecmp.cmp(input_fname, output_fname)
        self.assertEqual(diff, True)

        # remove generated files
        os.unlink(input_fname)
        os.unlink(output_fname)

if __name__ == '__main__':
    unittest.main()
