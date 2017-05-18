import sys
import time
import errno
import socket
import tempfile
import argparse
import os
from os import path
from subprocess import call
import project_root


def get_open_port():
    s = socket.socket(socket.AF_INET)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return str(port)


def curr_time_sec():
    return int(time.time())


def apply_patch(patch_name, repo_dir):
    patch = path.join(project_root.DIR, 'src', 'patches', patch_name)

    if call(['git', 'apply', patch], cwd=repo_dir) != 0:
        sys.stderr.write('patch apply failed but assuming things okay '
                         '(patch applied previously?)\n')


def make_sure_path_exists(target_path):
    try:
        os.makedirs(target_path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


TMPDIR = path.join(tempfile.gettempdir(), 'pantheon-tmp')
make_sure_path_exists(TMPDIR)


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
        'build', help='build the scheme')
    subparsers.add_parser(
        'init', help='initialize the scheme after building')

    receiver_parser = subparsers.add_parser('receiver', help='run receiver')
    sender_parser = subparsers.add_parser('sender', help='run sender')

    if run_first == 'receiver_first':
        sender_parser.add_argument(
            'ip', metavar='IP', help='IP address of receiver')
        sender_parser.add_argument('port', help='port of receiver')
    else:
        receiver_parser.add_argument(
            'ip', metavar='IP', help='IP address of sender')
        receiver_parser.add_argument('port', help='port of sender')

    args = parser.parse_args()
    return args
