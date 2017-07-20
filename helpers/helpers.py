import sys
import os
from os import path
import subprocess
from subprocess import PIPE
import socket
import signal
import errno
import tempfile
from time import strftime
import yaml
import project_root


def get_open_port():
    sock = socket.socket(socket.AF_INET)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    return str(port)


def make_sure_path_exists(target_path):
    try:
        os.makedirs(target_path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


TMPDIR = path.join(tempfile.gettempdir(), 'pantheon-tmp')
make_sure_path_exists(TMPDIR)


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
            sys.stderr.write('kill_proc_group: killed process group with pgid '
                             '%s\n' % os.getpgid(proc.pid))
            os.killpg(os.getpgid(proc.pid), signum)
        except OSError as exception:
            sys.stderr.write('kill_proc_group: %s\n' % exception)


def get_kernel_attr(sh_cmd, ssh_cmd=None, debug=True):
    if ssh_cmd is not None:
        kernel_attr = check_output(ssh_cmd + [sh_cmd])
    else:
        kernel_attr = check_output(sh_cmd, shell=True)

    if debug:
        is_local = 'local' if ssh_cmd is None else 'remote'
        sys.stderr.write('Got %s %s' % (is_local, kernel_attr))

    kernel_attr = kernel_attr.split('=')[-1].strip()
    return kernel_attr

def set_kernel_attr(sh_cmd, ssh_cmd=None, debug=True):
    if ssh_cmd is not None:
        res = call(ssh_cmd + [sh_cmd])
    else:
        res = call(sh_cmd, shell=True)

    if debug:
        is_local = 'local' if ssh_cmd is None else 'remote'
        attr, val = sh_cmd.split()[-1].split('=')
        if res != 0:
            sys.stderr.write('Failed: %s %s to %s\n' % (is_local, attr, val))
        else:
            sys.stderr.write('Set %s %s to %s\n' % (is_local, attr, val))


def get_default_qdisc(ssh_cmd=None, debug=True):
    sh_cmd = 'sysctl net.core.default_qdisc'
    local_qdisc = get_kernel_attr(sh_cmd, debug=debug)

    if ssh_cmd is not None:
        remote_qdisc = get_kernel_attr(sh_cmd, ssh_cmd, debug)
        if local_qdisc != remote_qdisc:
            sys.exit('default_qdisc differs on local and remote sides')

    return local_qdisc


def set_default_qdisc(qdisc, ssh_cmd=None, debug=True):
    sh_cmd = 'sudo sysctl -w net.core.default_qdisc=%s' % qdisc
    set_kernel_attr(sh_cmd, ssh_cmd, debug)
