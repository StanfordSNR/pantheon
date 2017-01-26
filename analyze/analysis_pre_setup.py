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

    # install texlive
    cmd1 = ('sudo apt-get -yq --force-yes install texlive')

    # install python packages
    cmd2 = ('sudo apt-get -yq --force-yes install '
            'python-matplotlib python-numpy python-tabulate')
    try:
        check_call(cmd1, shell=True)
        check_call(cmd2, shell=True)
    except:
        sys.stderr.write(
            'Warning: some dependencies may not be installed properly\n')

    install_pantheon_tunnel()


if __name__ == '__main__':
    main()
