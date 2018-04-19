#!/usr/bin/env python

from os import path
import project_root
from helpers.helpers import check_call

def get_sample_config(config_name):
    if config_name == 'bbr-cubic':
        config = ('test-name: test-bbr \n'
                  'runtime: 30 \n'
                  'interval: 1 \n'
                  'random_order: true \n'
                  'extra_mm_link_args: --uplink-queue=droptail '
                  '--uplink-queue-args=packets=512 \n'
                  'prepend_mm_cmds: mm-delay 30 \n'
                  'flows: \n'
                  '  - scheme: bbr \n'
                  '  - scheme: default_tcp # cubic ')

    elif config_name == 'verus-cubic':
        config = ('test-name: test-bbr \n'
                  'runtime: 30 \n'
                  'interval: 1 \n'
                  'random_order: true \n'
                  'extra_mm_link_args: --uplink-queue=droptail '
                  '--uplink-queue-args=packets=512 \n'
                  'prepend_mm_cmds: mm-delay 30 \n'
                  'flows: \n'
                  '  - scheme: verus \n'
                  '  - scheme: default_tcp # cubic ')
               
    with open('/tmp/pantheon-tmp/{}.yml'.format(config_name), 'w') as f:
        f.write(config)
        
    return '/tmp/pantheon-tmp/{}.yml'.format(config_name)

def main():
    curr_dir = path.dirname(path.abspath(__file__))
    data_trace = path.join(curr_dir, '12mbps_data.trace')
    ack_trace = path.join(curr_dir, '12mbps_ack.trace')

    test_py = path.join(project_root.DIR, 'test', 'test.py')

    """
    # test a receiver-first scheme --- default_tcp
    cc = 'default_tcp'

    cmd = ['python', test_py, 'local', '-t', '5', '-f', '0',
           '--uplink-trace', data_trace, '--downlink-trace', ack_trace,
           '--pkill-cleanup', '--schemes', '%s' % cc]
    check_call(cmd)

    cmd = ['python', test_py, 'local', '-t', '5', '-f', '1',
           '--uplink-trace', data_trace, '--downlink-trace', ack_trace,
           '--pkill-cleanup', '--schemes', '%s' % cc]
    check_call(cmd)

    cmd = ['python', test_py, 'local', '-t', '5', '-f', '1',
           '--run-times', '2', '--uplink-trace', data_trace,
           '--downlink-trace', ack_trace, '--pkill-cleanup',
           '--schemes', '%s' % cc]
    check_call(cmd)

    cmd = ['python', test_py, 'local', '-t', '5', '-f', '2', '--interval', '2',
           '--uplink-trace', data_trace, '--downlink-trace', ack_trace,
           '--pkill-cleanup', '--schemes', '%s' % cc]
    check_call(cmd)

    cmd = ['python', test_py, 'local', '-t', '5', '--pkill-cleanup',
           '--uplink-trace', data_trace,
           '--downlink-trace', ack_trace,
           '--extra-mm-link-args',
           '--uplink-queue=droptail --uplink-queue-args=packets=200',
           '--prepend-mm-cmds', 'mm-delay 10',
           '--append-mm-cmds', 'mm-delay 10',
           '--schemes', '%s' % cc]
    check_call(cmd)

    # test a sender-first scheme --- verus
    cc = 'verus'

    cmd = ['python', test_py, 'local', '-t', '5', '-f', '0',
           '--uplink-trace', data_trace, '--downlink-trace', ack_trace,
           '--pkill-cleanup', '--schemes', '%s' % cc]
    check_call(cmd)

    cmd = ['python', test_py, 'local', '-t', '5', '-f', '1',
           '--uplink-trace', data_trace, '--downlink-trace', ack_trace,
           '--pkill-cleanup', '--schemes', '%s' % cc]
    check_call(cmd)
    """

    # test running with a config file -- two reciever first schemes
    config = get_sample_config('bbr-cubic')
    cmd = ['python', test_py, '-c', config, 'local',
           '--uplink-trace', data_trace, '--downlink-trace', ack_trace,
           '--pkill-cleanup']
    check_call(cmd)
    
    # test running with a config file -- one receiver first, one sender first scheme
    config = get_sample_config('verus-cubic')
    cmd = ['python', test_py, '-c', config, 'local',
           '--uplink-trace', data_trace, '--downlink-trace', ack_trace,
           '--pkill-cleanup']
    check_call(cmd)
    

if __name__ == '__main__':
    main()
