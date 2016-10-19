#!/usr/bin/python

import os
import sys
import unittest
from os import path
from parse_arguments import parse_arguments
from subprocess import check_call, check_output


class TestCongestionControl(unittest.TestCase):
    def __init__(self, test_name, args):
        super(TestCongestionControl, self).__init__(test_name)
        self.cc = args.cc.lower()
        self.remote = args.remote
        self.private_key = args.private_key

    def setup(self):
        self.test_dir = path.abspath(path.dirname(__file__))
        src_dir = path.abspath(path.join(self.test_dir, '../src'))
        self.src_file = path.join(src_dir, self.cc + '.py')

        if self.remote:
            (self.remote_addr, self.remote_dir) = self.remote.split(':')

            self.ssh_cmd = ['ssh']
            if self.private_key:
                self.ssh_cmd += ['-i', self.private_key]
            self.ssh_cmd.append(self.remote_addr)

            self.remote_ip = self.remote_addr.split('@')[-1]
            remote_src_dir = path.join(self.remote_dir, 'src')
            self.src_file = path.join(remote_src_dir, self.cc + '.py')

        # Enable IP forwarding
        sysctl_cmd = 'sudo sysctl -w net.ipv4.ip_forward=1'
        if self.remote:
            sysctl_cmd = ' '.join(self.ssh_cmd) + ' ' + sysctl_cmd
        sys.stderr.write('+ ' + sysctl_cmd + '\n')
        check_call(sysctl_cmd, shell=True)

    def install(self):
        deps_cmd = ['python', self.src_file, 'deps']
        if self.remote:
            deps_cmd = self.ssh_cmd + deps_cmd
        sys.stderr.write('+ ' + ' '.join(deps_cmd) + '\n')
        deps_needed = check_output(deps_cmd)

        if deps_needed:
            sys.stderr.write('Installing dependencies...\n')
            sys.stderr.write(deps_needed)
            install_cmd = 'sudo apt-get -yq --force-yes install ' + deps_needed
            if self.remote:
                install_cmd = ' '.join(self.ssh_cmd) + ' ' + install_cmd
            check_call(install_cmd, shell=True)
        sys.stderr.write('Done\n')

    def build(self):
        build_cmd = ['python', self.src_file, 'build']
        if self.remote:
            build_cmd = self.ssh_cmd + build_cmd
        sys.stderr.write('+ ' + ' '.join(build_cmd) + '\n')
        sys.stderr.write('Building...\n')
        check_call(build_cmd)
        sys.stderr.write('Done\n')

    def initialize(self):
        init_cmd = ['python', self.src_file, 'initialize']
        if self.remote:
            init_cmd = self.ssh_cmd + init_cmd
        sys.stderr.write('+ ' + ' '.join(init_cmd) + '\n')
        sys.stderr.write('Performing intialization commands...\n')
        check_call(init_cmd)
        sys.stderr.write('Done\n')

    # congestion control setup
    def test_congestion_control_setup(self):
        # local or remote setup before running setup tests
        self.setup()

        # get build dependencies
        self.install()

        # run build commands
        self.build()

        # run initialize commands
        self.initialize()


def main():
    args = parse_arguments(path.basename(__file__))

    # create test suite to run
    suite = unittest.TestSuite()
    suite.addTest(TestCongestionControl('test_congestion_control_setup', args))
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)


if __name__ == '__main__':
    main()
