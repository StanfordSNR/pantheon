import sys
import os
from os import path
import subprocess
from subprocess import PIPE
import signal
from time import strftime
import yaml
import project_root
from parse_arguments import parse_remote, parse_arguments
from src.helpers import make_sure_path_exists, get_open_port, TMPDIR


def print_cmd(cmd):
    if isinstance(cmd, list):
        cmd_to_print = ' '.join(cmd).strip()
    elif isinstance(cmd, str):
        cmd_to_print = cmd.strip()

    sys.stderr.write('$ ' + cmd_to_print + '\n')


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


def kill_proc_group(proc):
    if proc:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except OSError as exception:
            sys.stderr.write('%s\n' % exception)
