#!/usr/bin/env python

import os
import sys
import signal
import subprocess
from subprocess import Popen, PIPE, check_output


def destroy(procs):
    for proc in procs.itervalues():
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)

    sys.exit(0)


def main():
    procs = {}

    while True:
        raw_cmd = sys.stdin.readline()
        cmd = raw_cmd.split()

        if cmd[0] == 'tunnel':
            if len(cmd) < 3:
                sys.stderr.write('Unknown command: ' + raw_cmd)
                continue

            tun_id = int(cmd[1]) - 1
            cmd_to_run = ' '.join(cmd[2:])

            if cmd[2] == 'mm-tunnelclient' or cmd[2] == 'mm-tunnelserver':
                proc = Popen(cmd_to_run, stdin=PIPE, stdout=PIPE, shell=True,
                             preexec_fn=os.setsid)
                procs[tun_id] = proc
            elif cmd[2] == 'python':
                procs[tun_id].stdin.write(cmd_to_run + '\n')
            elif cmd[2] == 'readline':
                sys.stdout.write(procs[tun_id].stdout.readline())
                sys.stdout.flush()
            else:
                sys.stderr.write('Unknown command: ' + raw_cmd)
                continue
        elif cmd[0] == 'ntpdate':
            if len(cmd) != 3:
                sys.stderr.write('Unknown command: ' + raw_cmd)
                continue

            ntp_output = check_output(cmd)
            offset = ntp_output.rsplit(' ', 2)[-2]

            try:
                float(offset)
            except:
                sys.stderr.write('Failed to get clock offset from ntpdate\n')
                sys.stderr.write(ntp_output)
                sys.stdout.write('error\n')
            else:
                sys.stdout.write(offset + '\n')
            sys.stdout.flush()
        elif cmd[0] == 'halt':
            destroy(procs)
        else:
            sys.stderr.write('Unknown command: ' + raw_cmd)
            continue


if __name__ == '__main__':
    main()
