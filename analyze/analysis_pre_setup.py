#!/usr/bin/env python

import os
import sys
import pantheon_helpers
from os import path
from helpers.parse_arguments import parse_arguments
from helpers.pantheon_help import check_call, make_sure_path_exists


def main():
    # prepare /tmp/pantheon-tmp
    make_sure_path_exists('/tmp/pantheon-tmp')

    # install texlive, matplotlib, etc.
    cmd = ('sudo apt-get -yq --force-yes install '
           'texlive python-matplotlib')
    check_call(cmd, shell=True)

    # TODO install mahimahi

if __name__ == '__main__':
    main()
