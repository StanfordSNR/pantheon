#!/usr/bin/env python

import os
import sys
import pantheon_helpers
from os import path
from helpers.parse_arguments import parse_arguments
from helpers.pantheon_help import (call, check_call, check_output,
                                   parse_remote, sanity_check_gitmodules)


class Setup:
    def __init__(self, args):
        self.cc = args.cc.lower()
        self.remote = args.remote
        self.test_dir = path.abspath(path.dirname(__file__))
        sanity_check_gitmodules()

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
    def setup(self):
        self.setup_congestion_control()

        # run remote setup.py
        if self.remote:
            rd = parse_remote(self.remote)
            cmd = rd['ssh_cmd'] + ['python', rd['setup'], self.cc]
            check_call(cmd)


def main():
    args = parse_arguments(path.basename(__file__))

    setup = Setup(args)
    setup.setup()


if __name__ == '__main__':
    DEVNULL = open(os.devnull, 'w')
    main()
    DEVNULL.close()
