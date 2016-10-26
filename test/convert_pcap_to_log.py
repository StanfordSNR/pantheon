#!/usr/bin/python

import argparse
import pyshark
import os
from pprint import pprint


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'pcap', help='pcap file captured by tcpdump')
    parser.add_argument(
        'cc', metavar='congestion-control',
        help='congestion control scheme that generated the pcap files')
    parser.add_argument(
        'role', choices=['server', 'client'],
        help='server or client')
    parser.add_argument(
        'server_port', metavar='server-port', type=int,
        help='the port that server is listening to')
    parser.add_argument(
        '-i', metavar='INGRESS-LOG', action='store', dest='ingress_log',
        required=True, help='ingress log to save')
    parser.add_argument(
        '-e', metavar='EGRESS-LOG', action='store', dest='egress_log',
        required=True, help='egress log to save')

    return parser.parse_args()


def get_ingress_uid(pkt, cc, role):
    pass


def get_egress_uid(pkt, cc, role):
    pass


def main():
    args = parse_arguments()

    ingress_log = open(args.ingress_log, 'w')
    egress_log = open(args.egress_log, 'w')

    init_ts = -1
    pcap = pyshark.FileCapture(os.path.abspath(args.pcap))
    for pkt in pcap:
        ts = int(round(float(pkt.sniff_timestamp) * 1000))
        if init_ts == -1:
            init_ts = ts
            ingress_log.write('# ingress: %s\n' % init_ts)
            egress_log.write('# egress: %s\n' % init_ts)

        ts -= init_ts
        size = int(pkt.ip.len)

        src_port = int(pkt.udp.srcport)
        dst_port = int(pkt.udp.dstport)
        if (args.role == 'client' and src_port == server_port or
                args.role == 'server' and dst_port == server_port):
            uid = get_ingress_uid(pkt, args.cc, args.role)
            ingress_log.write('%s - %s - %s\n' % (ts, uid, size))
        elif (args.role == 'server' and src_port == server_port or
                args.role == 'client' and dst_port == server_port):
            uid = get_egress_uid(pkt, args.cc, args.role)
            egress_log.write('%s - %s - %s\n' % (ts, uid, size))

    ingress_log.close()
    egress_log.close()


if __name__ == '__main__':
    main()
