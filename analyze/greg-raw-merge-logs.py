#!/usr/bin/env python

import sys
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-i', action='store', metavar='INGRESS-LOG', dest='ingress_log',
        required=True, help='ingress log of a tunnel')
    parser.add_argument(
        '-e', action='store', metavar='EGRESS-LOG', dest='egress_log',
        required=True, help='egress log of a tunnel')
    parser.add_argument(
        '-o', action='store', metavar='OUTPUT-LOG', dest='output_log',
        required=True, help='tunnel log after merging')

    return parser.parse_args()


def parse_line(line, time_calibration_offset):
    (ts, uid, size) = line.split('-')
    return (float(ts) + time_calibration_offset, int(uid), int(size))


def single_mode(args):
    recv_log = open(args.ingress_log)
    send_log = open(args.egress_log)
    output_log = open(args.output_log, 'w')

    # retrieve initial timestamp of sender from the first line
    line = send_log.readline()
    if not line:
        warning = 'Warning: egress log is empty\n'
        sys.stderr.write(warning)
        exit(0)

    send_init_ts = float(line.rsplit(':', 1)[-1])
    min_init_ts = send_init_ts

    # retrieve initial timestamp of receiver from the first line
    line = recv_log.readline()
    if not line:
        warning = 'Warning: ingress log is empty\n'
        sys.stderr.write(warning)
        exit(0)

    recv_init_ts = float(line.rsplit(':', 1)[-1])
    if recv_init_ts < min_init_ts:
        min_init_ts = recv_init_ts

    #output_log.write('# init timestamp: %.3f\n' % min_init_ts)

    # timestamp calibration to ensure non-negative timestamps
    send_calibration_offset = send_init_ts - min_init_ts
    recv_calibration_offset = recv_init_ts - min_init_ts

    # construct a hash table using uid as keys
    send_pkts = {}
    for line in send_log:
        (send_ts, send_uid, send_size) = parse_line(line, send_calibration_offset)
        assert send_uid not in send_pkts
        send_pkts[send_uid] = (send_ts, send_size)

    send_log.seek(0)
    send_log.readline()

    # construct a set of received uids
    recv_pkts = {}
    for line in recv_log:
        (recv_ts, recv_uid, recv_size) = parse_line(line, recv_calibration_offset)
        assert recv_uid not in recv_pkts
        recv_pkts[recv_uid] = recv_ts

    recv_log.seek(0)
    recv_log.readline()

    # merge two sorted logs into one
    send_line = send_log.readline()
    if send_line:
        (send_ts, send_uid, send_size) = parse_line(send_line, send_calibration_offset)

    recv_line = recv_log.readline()
    if recv_line:
        (recv_ts, recv_uid, recv_size) = parse_line(recv_line, recv_calibration_offset)

    while send_line or recv_line:
        if (send_line and recv_line and send_ts <= recv_ts) or not recv_line:
            if send_uid in recv_pkts:
                prop_delay = recv_pkts[send_uid] - send_ts
                output_log.write('%.3f %.3f %d\n' % (send_ts, prop_delay, send_size))
            else:
                output_log.write('%.3f NaN %d\n' % (send_ts, send_size))

            #output_log.write('%.3f + %s\n' % (send_ts, send_size))
            send_line = send_log.readline()
            if send_line:
                (send_ts, send_uid, send_size) = parse_line(send_line, send_calibration_offset)
        elif (send_line and recv_line and send_ts > recv_ts) or not send_line:
            if recv_uid in send_pkts:
                (paired_send_ts, paired_send_size) = send_pkts[recv_uid]
                # inconsistent packet size
                if paired_send_size != recv_size:
                    warning = (
                        'Warning: packet %s came into tunnel with size %s '
                        'but left with size %s\n' %
                        (recv_uid, paired_send_size, recv_size))
                    sys.stderr.write(warning)
                    exit(0)
            else:
                # nonexistent packet
                warning = ('Warning: received a packet with nonexistent uid '
                           '%s\n' % recv_uid)
                sys.stderr.write(warning)
                exit(0)

            delay = recv_ts - paired_send_ts
            #output_log.write('%.3f %.3f\n'
            #                 % (recv_ts, delay))
            recv_line = recv_log.readline()
            if recv_line:
                (recv_ts, recv_uid, recv_size) = parse_line(recv_line, recv_calibration_offset)

    recv_log.close()
    send_log.close()
    output_log.close()

def main():
    args = parse_arguments()
    single_mode(args)

if __name__ == '__main__':
    main()
