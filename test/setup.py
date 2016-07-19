#!/usr/bin/python

import os, sys, unittest
from subprocess import Popen, PIPE, check_call, check_output

# print setup usage
def usage():
    print 'Usage:'
    print './setup.py <congestion-control-name>'
    sys.exit(1)

class TestCongestionControl(unittest.TestCase):
    def install(self):
        deps_cmd = 'python %s deps' % self.src_file
        sys.stderr.write('+ ' + deps_cmd + '\n')
        deps_needed = check_output(deps_cmd, shell=True)
        if deps_needed:
            sys.stderr.write('Installing dependencies...\n')
            sys.stderr.write(deps_needed)
            install_cmd = 'sudo apt-get -yq --force-yes install ' + deps_needed
            check_call(install_cmd , shell=True)
        sys.stderr.write('Done\n')

    def build(self):
        build_cmd = 'python %s build' % self.src_file
        sys.stderr.write('+ ' + build_cmd + '\n')
        sys.stderr.write('Building...\n')
        check_call(build_cmd, shell=True)
        sys.stderr.write('Done\n')

    def initialize(self):
        initialize_cmd = 'python %s initialize' % self.src_file
        sys.stderr.write('+ ' + initialize_cmd + '\n')
        sys.stderr.write('Performing intialization commands...\n')
        check_call(initialize_cmd, shell=True)
        sys.stderr.write('Done\n')

    # congestion control setup
    def test_congestion_control_setup(self):
        self.cc_option = sys.argv[1].lower()
        self.test_dir = os.path.abspath(os.path.dirname(__file__))
        src_dir = os.path.abspath(os.path.join(self.test_dir, '../src'))
        self.src_file = os.path.join(src_dir, self.cc_option + '.py')

        # get build dependencies
        self.install()

        # run build commands
        self.build()

        # run initialize commands
        self.initialize()

def main():
    if len(sys.argv) != 2:
        usage()

    # Enable IP forwarding
    cmd = 'sudo sysctl -w net.ipv4.ip_forward=1'
    sys.stderr.write('+ ' + cmd + '\n')
    check_call(cmd, shell=True)

    # create test suite to run
    suite = unittest.TestSuite()
    suite.addTest(TestCongestionControl('test_congestion_control_setup'))
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)

if __name__ == '__main__':
    DEVNULL = open(os.devnull, 'wb')
    main()
    DEVNULL.close()
