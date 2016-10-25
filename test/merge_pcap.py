#!/usr/bin/python

import argparse


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

    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.output_log:
        output_log = open(args.output_log, 'w')
    else:
        output_log = sys.stdout


if __name__ == '__main__':
    main()
