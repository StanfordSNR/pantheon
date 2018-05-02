#!/usr/bin/env python

from os import path
import argparse

import context
from helpers.subprocess_wrappers import check_call


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('remote', metavar='HOSTADDR:PANTHEON-DIR')
    args = parser.parse_args()
    remote = args.remote

    test_py = path.join(context.src_dir, 'experiments', 'test.py')

    # test a receiver-first scheme --- cubic
    cc = 'cubic'

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

    # test a sender-first scheme --- verus
    cc = 'verus'

    cmd = ['python', test_py, 'remote', remote, '-t', '5', '--pkill-cleanup',
           '--schemes', cc]
    check_call(cmd)

    cmd = ['python', test_py, 'remote', remote, '-t', '5', '--pkill-cleanup',
           '--sender', 'remote', '--schemes', cc]
    check_call(cmd)


if __name__ == '__main__':
    main()
