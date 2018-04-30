#!/usr/bin/env python

import signal
import argparse

import context
from helpers import utils
from helpers.subprocess_wrappers import call


# prevent this script from being killed before cleaning up using pkill
def signal_handler(signum, frame):
    pass


def main():
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--kill-dir', metavar='DIR', help='kill all scripts in the directory')
    args = parser.parse_args()

    # kill mahimahi shells and iperf
    pkill = 'pkill -f '
    pkill_cmds = [pkill + 'mm-delay', pkill + 'mm-link', pkill + 'mm-loss',
                  pkill + 'mm-tunnelclient', pkill + 'mm-tunnelserver',
                  pkill + '-SIGKILL iperf']

    if args.kill_dir:
        pkill_cmds.append(pkill + args.kill_dir)

    for cmd in pkill_cmds:
        call(cmd, shell=True)


if __name__ == '__main__':
    main()
