import sys
import subprocess
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
