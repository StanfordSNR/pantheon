import sys
import time
import signal
import argparse
import os
from os import path
from subprocess import call
import project_root
from helpers.helpers import (
    make_sure_path_exists, TMPDIR, parse_config, get_default_qdisc)


def curr_time_sec():
    return int(time.time())


def check_default_qdisc(cc):
    config = parse_config()
    cc_config = config['schemes'][cc]
    kernel_qdisc = get_default_qdisc(debug=False)

    if 'qdisc' in cc_config:
        required_qdisc = cc_config['qdisc']
    else:
        required_qdisc = config['kernel_attrs']['default_qdisc']

    if kernel_qdisc != required_qdisc:
        sys.exit('Your default packet scheduler is "%s" currently. Please run '
                 '"sudo sysctl -w net.core.default_qdisc=%s" to use the '
                 'appropriate queueing discipline for %s to work, and change '
                 'it back after testing.'
                 % (kernel_qdisc, required_qdisc, cc_config['friendly_name']))


def apply_patch(patch_name, repo_dir):
    patch = path.join(project_root.DIR, 'src', 'patches', patch_name)

    if call(['git', 'apply', patch], cwd=repo_dir) != 0:
        sys.stderr.write('patch apply failed but assuming things okay '
                         '(patch applied previously?)\n')


def wait_and_kill_iperf(proc):
    def stop_signal_handler(signum, frame):
        if proc:
            os.kill(proc.pid, signal.SIGKILL)
            sys.stderr.write(
                'wait_and_kill_iperf: caught signal %s and killed iperf with '
                'pid %s\n' % (signum, proc.pid))

    signal.signal(signal.SIGINT, stop_signal_handler)
    signal.signal(signal.SIGTERM, stop_signal_handler)

    proc.wait()


def parse_arguments(run_first):
    if run_first != 'receiver_first' and run_first != 'sender_first':
        sys.exit('Specify "receiver_first" or "sender_first" '
                 'in parse_arguments()')

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='option')

    subparsers.add_parser(
        'deps', help='print a space-separated list of build dependencies')
    subparsers.add_parser(
        'run_first', help='print which side (sender or receiver) runs first')
    subparsers.add_parser(
        'setup', help='set up the scheme (required to be run at the first '
        'time; must make persistent changes across reboots)')
    subparsers.add_parser(
        'setup_after_reboot', help='set up the scheme (required to be run '
        'every time after reboot)')

    receiver_parser = subparsers.add_parser('receiver', help='run receiver')
    sender_parser = subparsers.add_parser('sender', help='run sender')

    if run_first == 'receiver_first':
        receiver_parser.add_argument('port', help='port to listen on')
        sender_parser.add_argument(
            'ip', metavar='IP', help='IP address of receiver')
        sender_parser.add_argument('port', help='port of receiver')
        sender_parser.add_argument('checkpoint', default='-1',
                help='checkpoint to use (default: "-1")')
    else:
        sender_parser.add_argument('port', help='port to listen on')
        sender_parser.add_argument('checkpoint', default='-1',
                help='checkpoint to use (default: "-1")')
        receiver_parser.add_argument(
            'ip', metavar='IP', help='IP address of sender')
        receiver_parser.add_argument('port', help='port of sender')


    args = parser.parse_args()
    return args
