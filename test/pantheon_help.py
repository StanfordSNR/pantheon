import os
import sys
import errno
import subprocess
from os import path
from subprocess import PIPE


def print_cmd(cmd):
    if type(cmd) == list:
        cmd_to_print = ' '.join(cmd).strip()
    elif type(cmd) == str:
        cmd_to_print = cmd.strip()

    sys.stderr.write('+ ' + cmd_to_print + '\n')


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


def parse_remote(remote, cc=None):
    assert remote, 'error in parse_remote: "remote" must be non-empty'

    rd = {}

    (rd['addr'], rd['root_dir']) = remote.split(':')
    rd['ip'] = rd['addr'].split('@')[-1]
    rd['ssh_cmd'] = ['ssh', rd['addr']]

    rd['src_dir'] = path.join(rd['root_dir'], 'src')
    rd['test_dir'] = path.join(rd['root_dir'], 'test')

    rd['pre_setup'] = path.join(rd['test_dir'], 'pre_setup.py')
    rd['setup'] = path.join(rd['test_dir'], 'setup.py')
    rd['tun_manager'] = path.join(rd['test_dir'], 'tunnel_manager.py')

    if cc:
        rd['cc_src'] = path.join(rd['src_dir'], cc + '.py')

    return rd


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
