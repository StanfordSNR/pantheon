#!/usr/bin/env python

from os import path
import project_root
from helpers.helpers import check_call


def main():
    curr_dir = path.abspath(path.dirname(__file__))
    data_dir = path.join(curr_dir, 'data')

    test_py = path.join(project_root.DIR, 'test', 'test.py')
    analyze_py = path.join(project_root.DIR, 'analysis', 'analyze.py')

    cmd = ['python', test_py, 'local', '--schemes',
           'default_tcp vegas ledbat pcc verus sprout webrtc'
           ' scream copa taova koho_cc calibrated_koho saturator',
           '-t', '10', '--data-dir', data_dir, '--pkill-cleanup']
    assert call(cmd) == 0

    cmd = ['python', analyze_py, '--data-dir', data_dir]
    assert call(cmd) == 0


if __name__ == '__main__':
    main()
