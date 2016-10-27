#!/usr/bin/env python

import os
import sys
import argparse
from os import path
from subprocess import check_call, check_output, Popen, PIPE


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--server-pcap', required=True, action='store', dest='server_pcap',
        metavar='FILENAME', help='pcap file captured on the server side')
    parser.add_argument(
        '--client-pcap', required=True, action='store', dest='client_pcap',
        metavar='FILENAME', help='pcap file captured on the client side')
    parser.add_argument(
        'cc', metavar='congestion-control', help='congestion control scheme')
    parser.add_argument(
        'server_port', metavar='server-port',
        help='the port that server is listening to')

    return parser.parse_args()


def main():
    args = parse_arguments()

    test_dir = path.abspath(path.dirname(__file__))
    cc_src = path.join(test_dir, '../src/%s.py' % args.cc)
    convert_pcap_file = path.join(test_dir, 'convert_pcap_to_log.py')

    # find out who goes first
    who_goes_first_cmd = ['python', cc_src, 'who_goes_first']
    sys.stderr.write('+ ' + ' '.join(who_goes_first_cmd) + '\n')
    who_goes_first_info = check_output(who_goes_first_cmd)
    first_to_run = who_goes_first_info.split(' ')[0].lower()

    # generate ingress and egress logs of server
    server_ilog = path.join(test_dir, args.cc + '_server.ilog')
    server_elog = path.join(test_dir, args.cc + '_server.elog')

    convert_cmd = [convert_pcap_file, '-i', server_ilog, '-e', server_elog,
                   args.server_pcap, 'server', args.server_port]
    sys.stderr.write('+ ' + ' '.join(convert_cmd) + '\n')
    check_call(convert_cmd)

    # generate ingress and egress logs of client
    client_ilog = path.join(test_dir, args.cc + '_client.ilog')
    client_elog = path.join(test_dir, args.cc + '_client.elog')

    convert_cmd = [convert_pcap_file, '-i', client_ilog, '-e', client_elog,
                   args.client_pcap, 'client', args.server_port]
    sys.stderr.write('+ ' + ' '.join(convert_cmd) + '\n')
    check_call(convert_cmd)

    # generate "raw" (without tunnel) datalink and acklink log
    datalink_log = path.join(test_dir, args.cc + '_raw_datalink.log')
    acklink_log = path.join(test_dir, args.cc + '_raw_acklink.log')

    if first_to_run == 'receiver':
        datalink_cmd = ['mm-tunnel-merge-logs', 'single', '-i', server_ilog,
                        '-e', client_elog, '-o', datalink_log]
        acklink_cmd = ['mm-tunnel-merge-logs', 'single', '-i', client_ilog,
                       '-e', server_elog, '-o', acklink_log]
    else:
        datalink_cmd = ['mm-tunnel-merge-logs', 'single', '-i', client_ilog,
                        '-e', server_elog, '-o', datalink_log]
        acklink_cmd = ['mm-tunnel-merge-logs', 'single', '-i', server_ilog,
                       '-e', client_elog, '-o', acklink_log]

    sys.stderr.write('+ ' + ' '.join(datalink_cmd) + '\n')
    check_call(datalink_cmd)

    sys.stderr.write('+ ' + ' '.join(acklink_cmd) + '\n')
    check_call(acklink_cmd)

    # generate statistical results
    throughput_cmd = 'mm-tunnel-throughput'
    delay_cmd = 'mm-tunnel-delay'

    datalink_throughput_svg = path.join(
        test_dir, '%s_raw_data_tput.svg' % args.cc)
    datalink_delay_svg = path.join(
        test_dir, '%s_raw_data_delay.svg' % args.cc)
    acklink_throughput_svg = path.join(
        test_dir, '%s_raw_ack_tput.svg' % args.cc)
    acklink_delay_svg = path.join(
        test_dir, '%s_raw_ack_delay.svg' % args.cc)

    stats_log = path.join(test_dir, '%s_raw_stats.log' % args.cc)
    stats = open(stats_log, 'w')

    sys.stderr.write('\n')
    # Data link
    # throughput
    datalink_throughput = open(datalink_throughput_svg, 'w')
    cmd = [throughput_cmd, '500', datalink_log]

    sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
    sys.stderr.write('* Data link statistics:\n')
    stats.write('* Data link statistics:\n')

    proc = Popen(cmd, stdout=datalink_throughput, stderr=PIPE)
    datalink_results = proc.communicate()[1]
    sys.stderr.write(datalink_results)
    stats.write(datalink_results)

    datalink_throughput.close()

    # delay
    datalink_delay = open(datalink_delay_svg, 'w')
    cmd = [delay_cmd, datalink_log]

    sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
    proc = Popen(cmd, stdout=datalink_delay, stderr=DEVNULL)
    proc.communicate()

    datalink_delay.close()

    sys.stderr.write('\n')
    # ACK link
    # throughput
    acklink_throughput = open(acklink_throughput_svg, 'w')
    cmd = [throughput_cmd, '500', acklink_log]

    sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
    sys.stderr.write('* ACK link statistics:\n')
    stats.write('* ACK link statistics:\n')

    proc = Popen(cmd, stdout=acklink_throughput, stderr=PIPE)
    acklink_results = proc.communicate()[1]
    sys.stderr.write(acklink_results)
    stats.write(acklink_results)

    acklink_throughput.close()

    # delay
    acklink_delay = open(acklink_delay_svg, 'w')
    cmd = [delay_cmd, acklink_log]

    sys.stderr.write('+ ' + ' '.join(cmd) + '\n')
    proc = Popen(cmd, stdout=acklink_delay, stderr=DEVNULL)
    proc.communicate()

    acklink_delay.close()

    stats.close()


if __name__ == '__main__':
    DEVNULL = open(os.devnull, 'w')
    main()
    DEVNULL.close()
