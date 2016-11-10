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
    prompt = ''

    while True:
        raw_cmd = sys.stdin.readline().strip()
        sys.stderr.write(prompt + raw_cmd + '\n')
        cmd = raw_cmd.split()

        if cmd[0] == 'tunnel':
            if len(cmd) < 3:
                sys.stderr.write('error: usage: tunnel ID CMD...\n')
                continue

            try:
                tun_id = int(cmd[1]) - 1
            except:
                sys.stderr.write('error: usage: tunnel ID CMD...\n')
                continue

            cmd_to_run = ' '.join(cmd[2:])

            if cmd[2] == 'mm-tunnelclient' or cmd[2] == 'mm-tunnelserver':
                cmd_to_run = os.path.expandvars(cmd_to_run).split()
                procs[tun_id] = Popen(cmd_to_run, stdin=PIPE, stdout=PIPE,
                                      preexec_fn=os.setsid)
            elif cmd[2] == 'python':
                procs[tun_id].stdin.write(cmd_to_run + '\n')
            elif cmd[2] == 'readline':
                if len(cmd) != 3:
                    sys.stderr.write('error: usage: tunnel ID readline\n')
                    continue

                sys.stdout.write(procs[tun_id].stdout.readline())
                sys.stdout.flush()
            else:
                sys.stderr.write('unknown command after "tunnel ID": %s\n'
                                 % cmd_to_run)
                continue
        elif cmd[0] == 'ntpdate':
            try:
                ntp_output = check_output(cmd)
            except:
                sys.stderr.write('invalid ntpdate command: %s\n' % raw_cmd)
                continue

            offset = ntp_output.rsplit(' ', 2)[-2]

            try:
                float(offset)
            except:
                sys.stderr.write('failed to get clock offset from ntpdate\n')
                sys.stderr.write(ntp_output)
                sys.stdout.write('error\n')
            else:
                sys.stdout.write(offset + '\n')
            sys.stdout.flush()
        elif cmd[0] == 'prompt':
            if len(cmd) != 2:
                sys.stderr.write('error: usage: prompt PROMPT\n')
                continue

            prompt = cmd[1].strip() + ' '
        elif cmd[0] == 'halt':
            if len(cmd) != 1:
                sys.stderr.write('error: usage: halt\n')
                continue

            destroy(procs)
        else:
            sys.stderr.write('unknown command: %s\n' % raw_cmd)
            continue


if __name__ == '__main__':
    main()
