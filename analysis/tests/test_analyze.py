#!/usr/bin/env python

from os import path
import project_root
from helpers.helpers import check_call


def main():
    curr_dir = path.abspath(path.dirname(__file__))
    data_dir = path.join(curr_dir, 'data')

    test_py = path.join(project_root.DIR, 'test', 'test.py')
    analyze_py = path.join(project_root.DIR, 'analysis', 'analyze.py')

    schemes = ('default_tcp vegas bbr ledbat pcc verus sprout webrtc '
               'scream copa taova koho_cc calibrated_koho saturator')
    cmd = ['python', test_py, 'local', '--schemes', schemes,
           '-t', '10', '--data-dir', data_dir, '--pkill-cleanup',
           '--prepend-mm-cmds', 'mm-delay 20', '--extra-mm-link-args',
           '--uplink-queue=droptail --uplink-queue-args=packets=200']
    check_call(cmd)

    cmd = ['python', analyze_py, '--data-dir', data_dir]
    check_call(cmd)


if __name__ == '__main__':
    main()
