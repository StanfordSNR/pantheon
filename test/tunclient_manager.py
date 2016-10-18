#!/usr/bin/python

import os
import sys
import signal
import argparse
import select
from subprocess import Popen, PIPE


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='store', dest='flows', type=int,
                        default=1, help='number of flows '
                        '(mm-tunnelclient/mm-tunnelserver pairs)')
    return parser.parse_args()


def destroy(tc_procs):
    for tc_proc in tc_procs:
        os.killpg(os.getpgid(tc_proc.pid), signal.SIGKILL)

    sys.exit(0)


def main():
    args = parse_arguments()
    flows = args.flows

    # prepare tunnelclient logs
    tc_ilogs = []
    tc_elogs = []
    for i in xrange(flows):
        tc_ilogs.append('/tmp/tc%s.ingress.log' % (i + 1))
        tc_elogs.append('/tmp/tc%s.egress.log' % (i + 1))

    # poller for sys.stdin
    poller = select.poll()
    poller.register(sys.stdin, select.POLLIN)

    # read "flows" lines from sys.stdin and connect to mm-tunnelserver
    tc_procs = []
    for i in xrange(flows):
        events = poller.poll(-1)

        for fd, flag in events:
            if fd == sys.stdin.fileno() and flag & select.POLLIN:
                tc_cmd = sys.stdin.readline().split()
                tc_cmd = tc_cmd + ['--ingress-log=' + tc_ilogs[i],
                                   '--egress-log=' + tc_elogs[i]]
                tc_proc = Popen(tc_cmd, stdin=PIPE, stdout=PIPE,
                                preexec_fn=os.setsid)
                tc_procs.append(tc_proc)

    while True:
        events = poller.poll(-1)

        for fd, flag in events:
            if fd == sys.stdin.fileno() and flag & select.POLLIN:
                cmd = sys.stdin.readline().strip()
                if cmd == 'halt':
                    destroy(tc_procs)


if __name__ == '__main__':
    main()
