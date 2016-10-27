#!/usr/bin/env python

import os
import sys
import argparse
from subprocess import check_call


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
        'server_port', metavar='server-port', type=int,
        help='the port that server is listening to')

    return parser.parse_args()


def main():
    args = parse_arguments()


if __name__ == '__main__':
    main()
