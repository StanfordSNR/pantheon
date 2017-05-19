#!/usr/bin/env python

import sys
import os
from os import path
from subprocess import call


def main():
    curr_dir = path.dirname(path.abspath(__file__))
    test_dir = path.abspath(path.join(curr_dir, os.pardir))
    test_py = path.join(test_dir, 'test.py')
    data_trace = path.join(curr_dir, '12mbps_data.trace')
    ack_trace = path.join(curr_dir, '12mbps_ack.trace')

    # test a receiver-first scheme
    cc = 'default_tcp'

    cmd = ['python', test_py, '-t', '5', '-f', '0',
           '--datalink-trace', data_trace,
           '--acklink-trace', ack_trace, cc]
    sys.stderr.write('$ %s\n' % ' '.join(cmd))
    assert call(cmd) == 0

    cmd = ['python', test_py, '-t', '5', '-f', '1',
           '--datalink-trace', data_trace,
           '--acklink-trace', ack_trace, cc]
    sys.stderr.write('$ %s\n' % ' '.join(cmd))
    assert call(cmd) == 0

    cmd = ['python', test_py, '-t', '5', '-f', '1', '--run-id', '2',
           '--datalink-trace', data_trace,
           '--acklink-trace', ack_trace, cc]
    sys.stderr.write('$ %s\n' % ' '.join(cmd))
    assert call(cmd) == 0

    cmd = ['python', test_py, '-t', '5', '-f', '2', '--interval', '2',
           '--datalink-trace', data_trace,
           '--acklink-trace', ack_trace, cc]
    sys.stderr.write('$ %s\n' % ' '.join(cmd))
    assert call(cmd) == 0

    cmd = ['python', test_py, '-t', '5',
           '--datalink-trace', data_trace,
           '--acklink-trace', ack_trace,
           '--extra-mm-link-args',
           '--uplink-queue=droptail --uplink-queue-args=packets=200',
           '--prepend-mm-cmds', 'mm-delay 10',
           '--append-mm-cmds', 'mm-delay 10', cc]
    sys.stderr.write('$ %s\n' % ' '.join(cmd))
    assert call(cmd) == 0

    # test a sender-first scheme
    cc = 'verus'

    cmd = ['python', test_py, '-t', '5', '-f', '0',
           '--datalink-trace', data_trace,
           '--acklink-trace', ack_trace, cc]
    sys.stderr.write('$ %s\n' % ' '.join(cmd))
    assert call(cmd) == 0

    cmd = ['python', test_py, '-t', '5', '-f', '1',
           '--datalink-trace', data_trace,
           '--acklink-trace', ack_trace, cc]
    sys.stderr.write('$ %s\n' % ' '.join(cmd))
    assert call(cmd) == 0


if __name__ == '__main__':
    main()
