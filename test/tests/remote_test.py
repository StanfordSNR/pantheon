#!/usr/bin/env python

import sys
import os
from os import path
import argparse
from subprocess import call


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('remote', metavar='HOSTADDR:PANTHEON-DIR')
    args = parser.parse_args()
    remote = args.remote

    curr_dir = path.dirname(path.abspath(__file__))
    test_dir = path.abspath(path.join(curr_dir, os.pardir))
    test_py = path.join(test_dir, 'test.py')

    # test a receiver-first scheme
    cc = 'default_tcp'

    cmd = ['python', test_py, '-r', remote, '-t', '5', cc]
    sys.stderr.write('$ %s\n' % ' '.join(cmd))
    assert call(cmd) == 0

    cmd = ['python', test_py, '-r', remote, '-t', '5',
           '--sender-side', 'remote', cc]
    sys.stderr.write('$ %s\n' % ' '.join(cmd))
    assert call(cmd) == 0

    cmd = ['python', test_py, '-r', remote, '-t', '5', '-f', '2',
           '--interval', '2', cc]
    sys.stderr.write('$ %s\n' % ' '.join(cmd))
    assert call(cmd) == 0

    # test a sender-first scheme
    cc = 'verus'

    cmd = ['python', test_py, '-r', remote, '-t', '5', cc]
    sys.stderr.write('$ %s\n' % ' '.join(cmd))
    assert call(cmd) == 0

    cmd = ['python', test_py, '-r', remote, '-t', '5',
           '--sender-side', 'remote', cc]
    sys.stderr.write('$ %s\n' % ' '.join(cmd))
    assert call(cmd) == 0


if __name__ == '__main__':
    main()
