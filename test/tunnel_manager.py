#!/usr/bin/python

import os
import sys
import signal
import select
from subprocess import Popen, PIPE


def destroy(procs):
    for proc in procs.itervalues():
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)

    sys.exit(0)


def main():
    procs = {}

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
                sh_cmd = ' '.join(cmd[2:])

                if cmd[2] == 'mm-tunnelclient' or 'mm-tunnelserver':
                    proc = Popen(sh_cmd, stdin=PIPE, stdout=PIPE,
                                 shell=True, preexec_fn=os.setsid)
                    procs[tun_id] = proc
                elif cmd[2] == 'python':
                    procs[tun_id].stdin.write(sh_cmd + '\n')
                elif cmd[2] == 'readline':
                    sys.stdout.write(procs[tun_id].stdout.readline())
                    sys.stdout.flush()
                else:
                    sys.stderr.write('Unknown command: %s\n' % ' '.join(cmd))
            elif cmd[0] == 'halt':
                destroy(procs)
            else:
                sys.stderr.write('Unknown command: %s\n' % ' '.join(cmd))


if __name__ == '__main__':
    main()
