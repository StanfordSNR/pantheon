import os
import sys
import errno
import subprocess
from os import path
from subprocess import PIPE


def sanity_check_gitmodules():
    third_party_dir = os.path.join(os.path.dirname(__file__), '../third_party')
    for module in os.listdir(third_party_dir):
        path = os.path.join(third_party_dir, module)
        if os.path.isdir(path):
            assert os.listdir(path), (
                    'Folder third_party/%s empty: make sure to initialize git '
                    'submodules with "git submodule update --init"' % module)


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


def get_friendly_names(cc_schemes):
    friendly_names = {}
    src_dir = path.abspath(path.join(path.dirname(__file__), '../src'))
    for cc in cc_schemes:
        cc_src = path.join(src_dir, cc + '.py')
        cc_name = check_output(['python', cc_src, 'friendly_name']).strip()
        friendly_names[cc] = cc_name if cc_name else cc
    return friendly_names


def install_pantheon_tunnel():
    third_party_dir = path.abspath(path.join(path.dirname(__file__),
                                             '../third_party'))
    mm_dir = path.join(third_party_dir, 'pantheon-tunnel')
    DEVNULL = open(os.devnull, 'w')

    mm_deps = (
        'debhelper autotools-dev dh-autoreconf iptables '
        'pkg-config '
        'iproute2 '
        'iptables iproute2')

    cmd = 'sudo apt-get -yq --force-yes install ' + mm_deps
    check_call(cmd, shell=True)

    cmd = ('cd %s && ./autogen.sh && ./configure && make -j4 && '
           'sudo make install' % mm_dir)
    check_call(cmd, shell=True)

    DEVNULL.close()
