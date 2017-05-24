#!/usr/bin/env python

from os import path
import argparse
import project_root
from helpers.helpers import check_call


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('remote', metavar='HOSTADDR:PANTHEON-DIR')
    args = parser.parse_args()
    remote = args.remote

    test_py = path.join(project_root.DIR, 'test', 'test.py')

    # test a receiver-first scheme
    cc = 'default_tcp'

    cmd = ['python', test_py, 'remote', remote, '--pkill-cleanup',
           '-t', '5', '--schemes', cc]
    check_call(cmd)

    cmd = ['python', test_py, 'remote', remote, '-t', '5', '--pkill-cleanup',
           '--run-times', '2', '--schemes', cc]
    check_call(cmd)

    cmd = ['python', test_py, 'remote', remote, '-t', '5', '--pkill-cleanup',
           '--sender', 'remote', '--schemes', cc]
    check_call(cmd)

    cmd = ['python', test_py, 'remote', remote, '-t', '5', '-f', '2',
           '--pkill-cleanup', '--interval', '2', '--schemes', cc]
    check_call(cmd)

    # test a sender-first scheme
    cc = 'verus'

    cmd = ['python', test_py, 'remote', remote, '-t', '5', '--pkill-cleanup',
           '--schemes', cc]
    check_call(cmd)

    cmd = ['python', test_py, 'remote', remote, '-t', '5', '--pkill-cleanup',
           '--sender', 'remote', '--schemes', cc]
    check_call(cmd)


if __name__ == '__main__':
    main()
