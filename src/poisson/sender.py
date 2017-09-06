#!/usr/bin/env python

import sys
import socket
import time
import random
import argparse


class Sender(object):
    def __init__(self, port, rate):
        self.lambd = 1e6 * max(1e-6, rate) / (8 * 1400)

        # UDP socket
        self.peer_addr = None

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0', port))
        sys.stderr.write('[sender] Listening on port %s\n' %
                         self.sock.getsockname()[1])

        # dummy data to send
        self.dummy_data = 'x' * 1400

    def cleanup(self):
        self.sock.close()

    def handshake(self):
        """Handshake with peer receiver. Must be called before run()."""

        while True:
            msg, addr = self.sock.recvfrom(1600)

            if msg == 'Hello from receiver' and self.peer_addr is None:
                self.peer_addr = addr
                self.sock.sendto('Hello from sender', self.peer_addr)
                sys.stderr.write('[sender] Handshake success! '
                                 'Receiver\'s address is %s:%s\n' % addr)
                break

    def run(self):
        while True:
            time.sleep(random.expovariate(self.lambd))
            self.sock.sendto(self.dummy_data, self.peer_addr)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int)
    parser.add_argument('--rate', metavar='Mbps', type=float, required=True)
    args = parser.parse_args()

    sender = Sender(args.port, args.rate)

    try:
        sender.handshake()
        sender.run()
    except KeyboardInterrupt:
        pass
    finally:
        sender.cleanup()


if __name__ == '__main__':
    main()
