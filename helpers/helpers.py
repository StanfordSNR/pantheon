import sys
import os
from os import path
import subprocess
import yaml
import project_root
from parse_arguments import parse_remote, parse_arguments
from src.helpers import make_sure_path_exists, pantheon_tmp, get_open_port


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


def sanity_check_gitmodules():
    third_party_dir = path.join(project_root.DIR, 'third_party')

    for module_dir in os.listdir(third_party_dir):
        module = path.join(third_party_dir, module_dir)
        if path.isdir(module):
            assert os.listdir(module), (
                'Folder third_party/%s empty: make sure to initialize git '
                'submodules with "git submodule update --init"' % module_dir)


def install_pantheon_tunnel():
    sys.stderr.write('Installing pantheon tunnel...\n')

    deps = ('debhelper autotools-dev dh-autoreconf iptables pkg-config '
            'iproute2 iptables iproute2')
    cmd = 'sudo apt-get -yq --force-yes install ' + deps
    check_call(cmd, shell=True)

    tunnel_repo = path.join(project_root.DIR, 'third_party', 'pantheon-tunnel')
    cmd = './autogen.sh && ./configure && make -j2 && sudo make install'
    check_call(cmd, shell=True, cwd=tunnel_repo)


def parse_config():
    config_path = path.join(project_root.DIR, 'src', 'config.yml')
    with open(config_path) as config_file:
        return yaml.load(config_file)
