#!/usr/bin/env python

import os
import sys
import unittest
from os import path
from parse_arguments import parse_arguments
from pantheon_help import call, check_call, check_output, parse_remote


class TestSetup(unittest.TestCase):
    def __init__(self, test_name, args):
        super(TestSetup, self).__init__(test_name)
        self.cc = args.cc.lower()
        self.remote = args.remote
        self.test_dir = path.abspath(path.dirname(__file__))

    def install(self):
        cmd = ['python', self.src_file, 'deps']
        deps = check_output(cmd).strip()

        if deps:
            sys.stderr.write('Installing dependencies...\n')
            cmd = 'sudo apt-get -yq --force-yes install ' + deps
            check_call(cmd, shell=True)

    def build(self):
        sys.stderr.write('Building...\n')
        cmd = ['python', self.src_file, 'build']
        check_call(cmd)

    def initialize(self):
        sys.stderr.write('Performing intialization commands...\n')
        cmd = ['python', self.src_file, 'init']
        check_call(cmd)

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
    def test_cc_setup(self):
        self.setup_congestion_control()

        # run remote setup.py
        if self.remote:
            rd = parse_remote(self.remote)
            cmd = rd['ssh_cmd'] + ['python', rd['setup'], self.cc]
            check_call(cmd)


def main():
    args = parse_arguments(path.basename(__file__))

    # create test suite to run
    suite = unittest.TestSuite()
    suite.addTest(TestSetup('test_cc_setup', args))
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)


if __name__ == '__main__':
    DEVNULL = open(os.devnull, 'w')
    main()
    DEVNULL.close()
