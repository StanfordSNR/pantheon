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
        'role', choices=['sender', 'receiver'],
        help='sender or receiver that generated the pcap file')
    parser.add_argument(
        '-i', metavar='INGRESS-LOG', action='store', dest='ingress_log',
        required=True, help='ingress log to save')
    parser.add_argument(
        '-e', metavar='EGRESS-LOG', action='store', dest='egress_log',
        required=True, help='egress log to save')

    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.role == 'sender':
        data_log = open(args.egress_log, 'w')
        ack_log = open(args.ingress_log, 'w')
    else:
        data_log = open(args.ingress_log, 'w')
        ack_log = open(args.egress_log, 'w')

    pcap = pyshark.FileCapture(os.path.abspath(args.pcap))
    for pkt in pcap:
        size = int(pkt.ip.len)
        pprint(vars(pkt))
        break

    data_log.close()
    ack_log.close()

if __name__ == '__main__':
    main()
