#!/usr/bin/env python

import os
import sys
import pantheon_helpers
from os import path
from helpers.parse_arguments import parse_arguments
from helpers.pantheon_help import (call, check_call, parse_remote,
                                   make_sure_path_exists)


class PreSetup:
    def __init__(self, args):
        self.remote = args.remote
        self.local_if = args.local_if
        self.remote_if = args.remote_if
        self.root_dir = path.abspath(path.join(path.dirname(__file__), '..'))
        self.third_party_dir = path.join(self.root_dir, 'third_party')

    def local_pre_setup(self):
        # update submodules
        cmd = ('cd %s && git submodule update --init --recursive' %
               self.root_dir)
        check_call(cmd, shell=True)

        # prepare /tmp/pantheon-tmp
        make_sure_path_exists('/tmp/pantheon-tmp')

        # Enable IP forwarding
        cmd = 'sudo sysctl -w net.ipv4.ip_forward=1'
        check_call(cmd, shell=True)

        # Disable Reverse Path Filter
        if self.local_if:
            rpf = ' /proc/sys/net/ipv4/conf/%s/rp_filter'
            cmd = 'echo 0 | sudo tee' + rpf % 'all' + rpf % self.local_if
            check_call(cmd, shell=True)

        # install texlive, matplotlib, etc.
        cmd = ('sudo apt-get -yq --force-yes install '
               'texlive python-matplotlib ntp ntpdate')
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

        cmd = ('cd %s && ./autogen.sh && ./configure && make -j && '
               'sudo make install' % mm_dir)
        check_call(cmd, shell=True)

    # congestion control pre-setup
    def pre_setup(self):
        sys.stderr.write('Performing local pre-setup...\n')
        self.local_pre_setup()

        # run remote pre_setup.py
        if self.remote:
            sys.stderr.write('\nPerforming remote pre-setup...\n')
            rd = parse_remote(self.remote)
            cmd = rd['ssh_cmd'] + ['python', rd['pre_setup']]
            if self.remote_if:
                cmd += ['--local-interface', self.remote_if]
            check_call(cmd)


def main():
    args = parse_arguments(path.basename(__file__))

    pre_setup = PreSetup(args)
    pre_setup.pre_setup()


if __name__ == '__main__':
    DEVNULL = open(os.devnull, 'w')
    main()
    DEVNULL.close()
