#!/usr/bin/env python

import os
import sys
import unittest
from os import path
from parse_arguments import parse_arguments
from subprocess_wrapper import call, check_call, check_output


class TestPreSetup(unittest.TestCase):
    def __init__(self, test_name, args):
        super(TestPreSetup, self).__init__(test_name)
        self.remote = args.remote
        self.local_if = args.local_if
        self.remote_if = args.remote_if
        self.third_party_dir = path.abspath(
            path.join(path.dirname(__file__), '../third_party'))

    def pre_setup(self):
        # update submodules
        cmd = 'git submodule update --init --recursive'
        check_call(cmd, shell=True)

        # Enable IP forwarding
        cmd = 'sudo sysctl -w net.ipv4.ip_forward=1'
        check_call(cmd, shell=True)

        # Disable Reverse Path Filter
        if self.local_if:
            rpf = ' /proc/sys/net/ipv4/conf/%s/rp_filter'
            cmd = 'echo 0 | sudo tee' + rpf % 'all' + rpf % self.local_if
            check_call(cmd, shell=True)

        # install texlive, matplotlib, etc.
        cmd = 'sudo apt-get -yq --force-yes install texlive python-matplotlib'
        check_call(cmd, shell=True)

        # install mahimahi
        mm_dir = path.join(self.third_party_dir, 'mahimahi')

        cmd = 'cd %s && sudo make install' % mm_dir
        if call(cmd, stdout=DEVNULL, shell=True) == 0:  # check if sufficient
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

    # congestion control pre-setup
    def test_cc_pre_setup(self):
        self.pre_setup()

        # run remote pre_setup.py
        if self.remote:
            (remote_addr, remote_dir) = self.remote.split(':')
            # can't use os.path.join since it only evaluates path locally
            if remote_dir[-1] != '/':
                remote_dir += '/'
            remote_setup = remote_dir + 'test/pre_setup.py'

            remote_setup_cmd = ['ssh', remote_addr, 'python', remote_setup]
            if self.remote_if:
                remote_setup_cmd += ['--local-interface', self.remote_if]
            check_call(remote_setup_cmd)


def main():
    args = parse_arguments(path.basename(__file__))

    # create test suite to run
    suite = unittest.TestSuite()
    suite.addTest(TestPreSetup('test_cc_pre_setup', args))
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)


if __name__ == '__main__':
    DEVNULL = open(os.devnull, 'w')
    main()
    DEVNULL.close()
