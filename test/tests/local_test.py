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

    cmd = ['python', test_py, 'local', '-t', '5', '-f', '0',
           '--uplink-trace', data_trace,
           '--downlink-trace', ack_trace, '--schemes', '%s' % cc]
    sys.stderr.write('$ %s\n' % ' '.join(cmd))
    assert call(cmd) == 0

    cmd = ['python', test_py, 'local', '-t', '5', '-f', '1',
           '--uplink-trace', data_trace,
           '--downlink-trace', ack_trace, '--schemes', '%s' % cc]
    sys.stderr.write('$ %s\n' % ' '.join(cmd))
    assert call(cmd) == 0

    cmd = ['python', test_py, 'local', '-t', '5', '-f', '1',
           '--run-times', '2', '--uplink-trace', data_trace,
           '--downlink-trace', ack_trace, '--schemes', '%s' % cc]
    sys.stderr.write('$ %s\n' % ' '.join(cmd))
    assert call(cmd) == 0

    cmd = ['python', test_py, 'local', '-t', '5', '-f', '2', '--interval', '2',
           '--uplink-trace', data_trace,
           '--downlink-trace', ack_trace, '--schemes', '%s' % cc]
    sys.stderr.write('$ %s\n' % ' '.join(cmd))
    assert call(cmd) == 0

    cmd = ['python', test_py, 'local', '-t', '5',
           '--uplink-trace', data_trace,
           '--downlink-trace', ack_trace,
           '--extra-mm-link-args',
           '--uplink-queue=droptail --uplink-queue-args=packets=200',
           '--prepend-mm-cmds', 'mm-delay 10',
           '--append-mm-cmds', 'mm-delay 10',
           '--schemes', '%s' % cc]
    sys.stderr.write('$ %s\n' % ' '.join(cmd))
    assert call(cmd) == 0

    # test a sender-first scheme
    cc = 'verus'

    cmd = ['python', test_py, 'local', '-t', '5', '-f', '0',
           '--uplink-trace', data_trace,
           '--downlink-trace', ack_trace, '--schemes', '%s' % cc]
    sys.stderr.write('$ %s\n' % ' '.join(cmd))
    assert call(cmd) == 0

    cmd = ['python', test_py, 'local', '-t', '5', '-f', '1',
           '--uplink-trace', data_trace,
           '--downlink-trace', ack_trace, '--schemes', '%s' % cc]
    sys.stderr.write('$ %s\n' % ' '.join(cmd))
    assert call(cmd) == 0


if __name__ == '__main__':
    main()
