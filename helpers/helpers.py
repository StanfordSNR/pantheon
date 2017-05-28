import sys
import os
from os import path
import subprocess
from subprocess import PIPE
import signal
from time import strftime
import yaml
import project_root
from src.helpers import make_sure_path_exists, get_open_port, TMPDIR


def print_cmd(cmd):
    if isinstance(cmd, list):
        cmd_to_print = ' '.join(cmd).strip()
    elif isinstance(cmd, str) or isinstance(cmd, unicode):
        cmd_to_print = cmd.strip()
    else:
        cmd_to_print = ''

    if cmd_to_print:
        sys.stderr.write('$ %s\n' % cmd_to_print)


def call(cmd, **kwargs):
    print_cmd(cmd)
    return subprocess.call(cmd, **kwargs)


def check_call(cmd, **kwargs):
    print_cmd(cmd)
    return subprocess.check_call(cmd, **kwargs)


def check_output(cmd, **kwargs):
    print_cmd(cmd)
    return subprocess.check_output(cmd, **kwargs)


def Popen(cmd, **kwargs):
    print_cmd(cmd)
    return subprocess.Popen(cmd, **kwargs)


def parse_config():
    with open(path.join(project_root.DIR, 'src', 'config.yml')) as config:
        return yaml.load(config)


def update_submodules():
    cmd = 'git submodule update --init --recursive'
    check_call(cmd, shell=True)


class TimeoutError(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutError()


def format_time():
    return strftime('%a, %d %b %Y %H:%M:%S %z')


def kill_proc_group(proc, signum=signal.SIGTERM):
    if proc:
        try:
            os.killpg(os.getpgid(proc.pid), signum)
        except OSError as exception:
            sys.stderr.write('%s\n' % exception)


def get_signal_for_cc(cc):
    # default_tcp and vegas run iperf, which often doesn't respond to SIGTERM
    if cc == 'default_tcp' or cc == 'vegas':
        return signal.SIGKILL
    else:
        return signal.SIGTERM
