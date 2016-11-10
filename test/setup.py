#!/usr/bin/env python

import os
import sys
import unittest
from os import path
from parse_arguments import parse_arguments
from subprocess_wrapper import call, check_call, check_output


class TestCongestionControl(unittest.TestCase):
    def __init__(self, test_name, args):
        super(TestCongestionControl, self).__init__(test_name)
        self.cc = args.cc.lower()
        self.remote = args.remote
        self.local_if = args.local_if
        self.remote_if = args.remote_if
        self.test_dir = path.abspath(path.dirname(__file__))

    def sanity_check_gitmodules(self):
        third_party_dir = os.path.join(self.test_dir, '../third_party')
        for module in os.listdir(third_party_dir):
            path = os.path.join(third_party_dir, module)
            if os.path.isdir(path):
                assert os.listdir(path), (
                    'Folder third_party/%s empty: make sure to initialize git '
                    'submodules with "git submodule update --init"' % module)

    def pre_setup(self):
        # Enable IP forwarding
        cmd = 'sudo sysctl -w net.ipv4.ip_forward=1'
        check_call(cmd, shell=True)

        # Disable Reverse Path Filter
        echo_cmd = 'echo 0 | sudo tee'
        filter_path = ' /proc/sys/net/ipv4/conf/%s/rp_filter'
        if self.local_if:
            cmd = echo_cmd + filter_path % 'all' + filter_path % self.local_if
            check_call(cmd, shell=True)

        if self.remote_if:
            cmd = echo_cmd + filter_path % 'all' + filter_path % self.remote_if
            cmd = ' '.join(self.ssh_cmd) + ' "%s"' % cmd
            check_call(cmd, shell=True)

        # install mahimahi
        mm_dir = path.join(self.test_dir, '../third_party/mahimahi')
        # make install alone sufficient if autogen.sh, configure already run
        cmd = 'cd %s && sudo make -j install' % mm_dir
        if call(cmd, stdout=DEVNULL, shell=True) is 0:
            return

        mm_deps = (
            'debhelper autotools-dev dh-autoreconf iptables protobuf-compiler '
            'libprotobuf-dev pkg-config libssl-dev dnsmasq-base ssl-cert '
            'libxcb-present-dev libcairo2-dev libpango1.0-dev iproute2 '
            'apache2-dev apache2-bin iptables dnsmasq-base gnuplot iproute2')

        cmd = 'sudo apt-get -yq --force-yes install ' + mm_deps
        check_call(cmd, shell=True)

        cmd = ('cd %s && ./autogen.sh && ./configure && make && '
               'sudo make install' % mm_dir)
        check_call(cmd, shell=True)

    def install(self):
        cmd = ['python', self.src_file, 'deps']
        deps = check_output(cmd).strip()

        if deps:
            sys.stderr.write('Installing dependencies...\n')
            cmd = 'sudo apt-get -yq --force-yes install ' + deps
            check_call(cmd, shell=True)
        sys.stderr.write('Done\n')

    def build(self):
        sys.stderr.write('Building...\n')
        cmd = ['python', self.src_file, 'build']
        check_call(cmd)
        sys.stderr.write('Done\n')

    def initialize(self):
        sys.stderr.write('Performing intialization commands...\n')
        cmd = ['python', self.src_file, 'init']
        check_call(cmd)
        sys.stderr.write('Done\n')

    def setup_congestion_control(self):
        src_dir = path.abspath(path.join(self.test_dir, '../src'))
        self.src_file = path.join(src_dir, self.cc + '.py')

        # get build dependencies
        self.install()

        # run build commands
        self.build()

        # run initialize commands
        self.initialize()

    # congestion control setup
    def test_congestion_control_setup(self):
        self.sanity_check_gitmodules()
        # run remote setup.py
        if self.remote:
            (remote_addr, remote_dir) = self.remote.split(':')
            self.ssh_cmd = ['ssh', remote_addr]

            # os.path.join evaluate path locally only
            if remote_dir[-1] != '/':
                remote_dir += '/'
            remote_setup = remote_dir + 'test/setup.py'
            remote_setup_cmd = self.ssh_cmd + ['python', remote_setup, self.cc]
            check_call(remote_setup_cmd)

        # run local setup.py (even when self.remote exists)

        # always enable IP forwarding, setup mahimahi and disable rp_filter
        self.pre_setup()

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
    DEVNULL = open(os.devnull, 'w')
    main()
    DEVNULL.close()
