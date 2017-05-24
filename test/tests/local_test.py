#!/usr/bin/env python

from os import path
import project_root
from helpers.helpers import call


def main():
    curr_dir = path.dirname(path.abspath(__file__))
    data_trace = path.join(curr_dir, '12mbps_data.trace')
    ack_trace = path.join(curr_dir, '12mbps_ack.trace')

    test_py = path.join(project_root.DIR, 'test', 'test.py')

    # test a receiver-first scheme
    cc = 'default_tcp'

    cmd = ['python', test_py, 'local', '-t', '5', '-f', '0',
           '--uplink-trace', data_trace, '--downlink-trace', ack_trace,
           '--pkill-cleanup', '--schemes', '%s' % cc]
    assert call(cmd) == 0

    cmd = ['python', test_py, 'local', '-t', '5', '-f', '1',
           '--uplink-trace', data_trace, '--downlink-trace',
           '--pkill-cleanup', ack_trace, '--schemes', '%s' % cc]
    assert call(cmd) == 0

    cmd = ['python', test_py, 'local', '-t', '5', '-f', '1',
           '--run-times', '2', '--uplink-trace', data_trace,
           '--downlink-trace', ack_trace, '--pkill-cleanup',
           '--schemes', '%s' % cc]
    assert call(cmd) == 0

    cmd = ['python', test_py, 'local', '-t', '5', '-f', '2', '--interval', '2',
           '--uplink-trace', data_trace, '--downlink-trace', ack_trace,
           '--pkill-cleanup', '--schemes', '%s' % cc]
    assert call(cmd) == 0

    cmd = ['python', test_py, 'local', '-t', '5', '--pkill-cleanup',
           '--uplink-trace', data_trace,
           '--downlink-trace', ack_trace,
           '--extra-mm-link-args',
           '--uplink-queue=droptail --uplink-queue-args=packets=200',
           '--prepend-mm-cmds', 'mm-delay 10',
           '--append-mm-cmds', 'mm-delay 10',
           '--schemes', '%s' % cc]
    assert call(cmd) == 0

    # test a sender-first scheme
    cc = 'verus'

    cmd = ['python', test_py, 'local', '-t', '5', '-f', '0',
           '--uplink-trace', data_trace,
           '--downlink-trace', ack_trace, '--schemes', '%s' % cc]
    assert call(cmd) == 0

    cmd = ['python', test_py, 'local', '-t', '5', '-f', '1',
           '--uplink-trace', data_trace,
           '--downlink-trace', ack_trace, '--schemes', '%s' % cc]
    assert call(cmd) == 0


if __name__ == '__main__':
    main()
