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
    tc_procs = [None] * flows
    tc_ilogs = []
    tc_elogs = []
    for i in xrange(flows):
        tc_ilogs.append('/tmp/tc%s.ingress.log' % (i + 1))
        tc_elogs.append('/tmp/tc%s.egress.log' % (i + 1))

    # poller for sys.stdin
    poller = select.poll()
    poller.register(sys.stdin, select.POLLIN)

    while True:
        events = poller.poll(-1)

        for fd, flag in events:
            if not (fd == sys.stdin.fileno() and flag & select.POLLIN):
                continue
            cmd = sys.stdin.readline().split()

            if cmd[0] == 'tunnel':
                tun_id = int(cmd[1]) - 1

                if cmd[2] == 'mm-tunnelclient':
                    tc_cmd = cmd[2:] + ['--ingress-log=' + tc_ilogs[tun_id],
                                        '--egress-log=' + tc_elogs[tun_id]]
                    tc_cmd = ' '.join(tc_cmd)
                    tc_proc = Popen(tc_cmd, stdin=PIPE, stdout=PIPE,
                                    shell=True, preexec_fn=os.setsid)
                    tc_procs[tun_id] = tc_proc
                elif cmd[2] == 'python':
                    tc_procs[tun_id].stdin.write(' '.join(cmd[2:]) + '\n')

            elif cmd[0] == 'halt':
                destroy(tc_procs)


if __name__ == '__main__':
    main()
