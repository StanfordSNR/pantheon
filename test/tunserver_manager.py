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


def destroy(ts_procs):
    for ts_proc in ts_procs:
        os.killpg(os.getpgid(ts_proc.pid), signal.SIGKILL)

    sys.exit(0)


def main():
    args = parse_arguments()
    flows = args.flows

    # prepare tunnelserver logs
    ts_procs = []
    ts_ilogs = []
    ts_elogs = []
    for i in xrange(flows):
        ts_ilogs.append('/tmp/ts%s.ingress.log' % (i + 1))
        ts_elogs.append('/tmp/ts%s.egress.log' % (i + 1))

    # run mm-tunnelserver
    for i in xrange(flows):
        ts_cmd = ['mm-tunnelserver', '--ingress-log=' + ts_ilogs[i],
                  '--egress-log=' + ts_elogs[i]]
        ts_proc = Popen(ts_cmd, stdin=PIPE, stdout=PIPE, preexec_fn=os.setsid)
        sys.stdout.write(ts_proc.stdout.readline())
        ts_procs.append(ts_proc)

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

                if cmd[2] == 'python':
                    ts_procs[tun_id].stdin.write(' '.join(cmd[2:]) + '\n')

            elif cmd[0] == 'halt':
                destroy(ts_procs)


if __name__ == '__main__':
    main()
