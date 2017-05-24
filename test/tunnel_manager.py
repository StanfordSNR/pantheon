#!/usr/bin/env python

import os
from os import path
import sys
import signal
from subprocess import Popen, PIPE
from colorama import Fore, Style
import project_root
from helpers.helpers import kill_proc_group, get_signal_for_cc


def main():
    prompt = ''
    procs = {}
    proc_signals = {}

    sys.stdout.write('tunnel manager is running\n')
    sys.stdout.flush()

    while True:
        input_cmd = sys.stdin.readline().strip()

        # print all the commands fed into tunnel manager
        if prompt:
            sys.stderr.write(Fore.BLUE + prompt + Style.RESET_ALL)
        sys.stderr.write(input_cmd + '\n')
        cmd = input_cmd.split()

        # manage I/O of multiple tunnels
        if cmd[0] == 'tunnel':
            if len(cmd) < 3:
                sys.stderr.write('error: usage: tunnel ID CMD...\n')
                continue

            try:
                tun_id = int(cmd[1]) - 1
            except ValueError:
                sys.stderr.write('error: usage: tunnel ID CMD...\n')
                continue

            cmd_to_run = ' '.join(cmd[2:])

            if cmd[2] == 'mm-tunnelclient' or cmd[2] == 'mm-tunnelserver':
                # expand $MAHIMAHI_BASE
                cmd_to_run = os.path.expandvars(cmd_to_run).split()
                procs[tun_id] = Popen(cmd_to_run, stdin=PIPE, stdout=PIPE,
                                      preexec_fn=os.setsid)
            elif cmd[2] == 'python':  # run python scripts inside tunnel
                if tun_id not in procs:
                    sys.stderr.write(
                        'error: run tunnel client or server first\n')

                procs[tun_id].stdin.write(cmd_to_run + '\n')

                cc = path.splitext(path.basename(cmd[3]))[0]
                proc_signals[tun_id] = get_signal_for_cc(cc)
            elif cmd[2] == 'readline':  # readline from stdout of tunnel
                if len(cmd) != 3:
                    sys.stderr.write('error: usage: tunnel ID readline\n')
                    continue

                if tun_id not in procs:
                    sys.stderr.write(
                        'error: run tunnel client or server first\n')

                sys.stdout.write(procs[tun_id].stdout.readline())
                sys.stdout.flush()
            else:
                sys.stderr.write('unknown command after "tunnel ID": %s\n'
                                 % cmd_to_run)
                continue
        elif cmd[0] == 'prompt':  # set prompt in front of commands to print
            if len(cmd) != 2:
                sys.stderr.write('error: usage: prompt PROMPT\n')
                continue

            prompt = cmd[1].strip() + ' '
        elif cmd[0] == 'halt':  # terminate all tunnel processes and quit
            if len(cmd) != 1:
                sys.stderr.write('error: usage: halt\n')
                continue

            for tun_id in procs:
                kill_proc_group(procs[tun_id], proc_signals[tun_id])

            sys.exit(0)
        else:
            sys.stderr.write('unknown command: %s\n' % input_cmd)
            continue


if __name__ == '__main__':
    main()
