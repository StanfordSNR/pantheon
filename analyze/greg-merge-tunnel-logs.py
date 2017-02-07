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


def parse_line(line):
    (ts, uid, size) = line.split('-')
    return (float(ts), int(uid), int(size))


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
    send_cal = send_init_ts - min_init_ts
    recv_cal = recv_init_ts - min_init_ts

    # construct a hash table using uid as keys
    send_pkts = {}
    for line in send_log:
        (send_ts, send_uid, send_size) = parse_line(line)
        send_pkts[send_uid] = (send_ts + send_cal, send_size)

    send_log.seek(0)
    send_log.readline()

    # construct a set of received uids
    recv_pkts = {}
    for line in recv_log:
        (recv_ts, recv_uid, recv_size) = parse_line(line)
        recv_pkts[recv_uid] = recv_ts + recv_cal

    recv_log.seek(0)
    recv_log.readline()

    # merge two sorted logs into one
    send_l = send_log.readline()
    if send_l:
        (send_ts, send_uid, send_size) = parse_line(send_l)

    recv_l = recv_log.readline()
    if recv_l:
        (recv_ts, recv_uid, recv_size) = parse_line(recv_l)

    while send_l or recv_l:
        if send_l:
            send_ts_cal = send_ts + send_cal
        if recv_l:
            recv_ts_cal = recv_ts + recv_cal

        if (send_l and recv_l and send_ts_cal <= recv_ts_cal) or not recv_l:
            if send_uid in recv_pkts:
                prop_delay = recv_pkts[send_uid] - send_ts_cal
                output_log.write('%.3f %.3f\n' % (send_ts_cal, prop_delay))
            else:
                output_log.write('%.3f lost\n' % send_ts_cal)

            #output_log.write('%.3f + %s\n' % (send_ts_cal, send_size))
            send_l = send_log.readline()
            if send_l:
                (send_ts, send_uid, send_size) = parse_line(send_l)
        elif (send_l and recv_l and send_ts_cal > recv_ts_cal) or not send_l:
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

            delay = recv_ts_cal - paired_send_ts
            #output_log.write('%.3f %.3f\n'
            #                 % (recv_ts_cal, delay))
            recv_l = recv_log.readline()
            if recv_l:
                (recv_ts, recv_uid, recv_size) = parse_line(recv_l)

    recv_log.close()
    send_log.close()
    output_log.close()

def main():
    args = parse_arguments()
    single_mode(args)

if __name__ == '__main__':
    main()
