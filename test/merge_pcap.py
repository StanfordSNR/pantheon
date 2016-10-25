#!/usr/bin/python

import argparse
import dpkt


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-s', metavar='SENDER-PCAP', action='store', dest='sender_pcap',
        required=True, help='pcap file captured on the sender side')
    parser.add_argument(
        '-r', metavar='RECEIVER-PCAP', action='store', dest='receiver_pcap',
        required=True, help='pcap file captured on the receiver side')
    parser.add_argument(
        '-o', metavar='OUTPUT-LOG', action='store', dest='output_log',
        help='log file merged from sender and receiver pcap files')
    parser.add_argument(
        'cc', metavar='congestion-control',
        help='congestion control scheme that generated the pcap files')

    return parser.parse_args()


def merge_pcap(send_pcap, recv_pcap, output_log, cc):
    pass


def main():
    args = parse_arguments()

    if args.output_log:
        output_log = open(args.output_log, 'w')
    else:
        output_log = sys.stdout

    sender_pcap = open(args.sender_pcap)
    send_pcap = dpkt.pcap.Reader(sender_pcap)

    receiver_pcap = open(args.receiver_pcap)
    recv_pcap = dpkt.pcap.Reader(receiver_pcap)

    merge_pcap(send_pcap, recv_pcap, output_log, args.cc)

    sender_pcap.close()
    receiver_pcap.close()

if __name__ == '__main__':
    main()
