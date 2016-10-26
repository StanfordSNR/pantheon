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
        self.test_dir = path.abspath(path.dirname(__file__))

    def sanity_check_gitmodules(self):
        third_party_dir = os.path.join(self.test_dir, '../third_party')
        for submodule in os.listdir(third_party_dir):
            path = os.path.join(third_party_dir, submodule)
            if os.path.isdir(path):
                assert os.listdir(path), 'Folder third_party/%s empty, make \
                    sure to initialize git submodules' % submodule

    def setup_mahimahi(self):
        # install mahimahi
        mm_deps = (
            'debhelper autotools-dev dh-autoreconf iptables protobuf-compiler '
            'libprotobuf-dev pkg-config libssl-dev dnsmasq-base ssl-cert '
            'libxcb-present-dev libcairo2-dev libpango1.0-dev iproute2 '
            'apache2-dev apache2-bin iptables dnsmasq-base gnuplot iproute2')

        cmd = 'sudo apt-get -yq --force-yes install ' + mm_deps
        sys.stderr.write('+ ' + cmd + '\n')
        check_call(cmd, shell=True)

        mm_dir = path.join(self.test_dir, '../third_party/mahimahi')
        cmd = ('cd %s && ./autogen.sh && ./configure && make && '
               'sudo make install' % mm_dir)
        sys.stderr.write('+ ' + cmd + '\n')
        check_call(cmd, shell=True)

        # Enable IP forwarding
        cmd = 'sudo sysctl -w net.ipv4.ip_forward=1'
        sys.stderr.write('+ ' + cmd + '\n')
        check_call(cmd, shell=True)

    def setup_congestion_control(self):
        src_dir = path.abspath(path.join(self.test_dir, '../src'))
        self.src_file = path.join(src_dir, self.cc + '.py')

        # get build dependencies
        self.install()

        # run build commands
        self.build()

        # run initialize commands
        self.initialize()

    def install(self):
        cmd = ['python', self.src_file, 'deps']
        sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
        deps = check_output(cmd)

        if deps:
            sys.stderr.write('Installing dependencies...\n')
            sys.stderr.write(deps)
            cmd = 'sudo apt-get -yq --force-yes install ' + deps
            sys.stderr.write('+ %s\n' % cmd)
            check_call(cmd, shell=True)
        sys.stderr.write('Done\n')

    def build(self):
        cmd = ['python', self.src_file, 'build']
        sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
        sys.stderr.write('Building...\n')
        check_call(cmd)
        sys.stderr.write('Done\n')

    def initialize(self):
        cmd = ['python', self.src_file, 'init']
        sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
        sys.stderr.write('Performing intialization commands...\n')
        check_call(cmd)
        sys.stderr.write('Done\n')

    # congestion control setup
    def test_congestion_control_setup(self):
        self.sanity_check_gitmodules()
        # run remote setup.py
        if self.remote:
            (remote_addr, remote_dir) = self.remote.split(':')
            ssh_cmd = ['ssh']
            if self.private_key:
                ssh_cmd += ['-i', self.private_key]
            ssh_cmd.append(remote_addr)

            # os.path.join evaluate path locally only
            if remote_dir[-1] != '/':
                remote_dir += '/'
            remote_setup = remote_dir + 'test/setup.py'
            ssh_cmd += ['python', remote_setup, self.cc]
            sys.stderr.write('+ ' + ' '.join(ssh_cmd) + '\n')
            check_call(ssh_cmd)

        # run local setup.py (even when self.remote exists)
        # setup mahimahi
        if self.cc == 'mahimahi':
            self.setup_mahimahi()
            return

        # setup congestion control scheme
        self.setup_congestion_control()


def main():
    args = parse_arguments(path.basename(__file__))

    # create test suite to run
    suite = unittest.TestSuite()
    suite.addTest(TestCongestionControl('test_congestion_control_setup', args))
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)


if __name__ == '__main__':
    main()
