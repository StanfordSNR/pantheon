#!/usr/bin/env python

import os
import sys
import pantheon_helpers
from os import path
from helpers.parse_arguments import parse_arguments
from helpers.pantheon_help import (check_call, make_sure_path_exists,
                                   install_pantheon_tunnel)


def main():
    # prepare /tmp/pantheon-tmp  to store .tex flie
    make_sure_path_exists('/tmp/pantheon-tmp')

    # install texlive, matplotlib, etc.
    cmd = ('sudo apt-get -yq --force-yes install '
           'texlive python-matplotlib python-numpy python-pip')
    try:
        check_call(cmd, shell=True)

        # install tabulate for compare_two_experiments.py
        check_call('sudo pip install tabulate', shell=True)
    except:
        sys.stderr.write(
            'Warning: some dependencies may not be installed properly\n')

    install_pantheon_tunnel()


if __name__ == '__main__':
    main()
