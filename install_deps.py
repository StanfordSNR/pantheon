#!/usr/bin/env python

from os import path
from subprocess import check_call


def main():
    # update submodules
    cmd = 'git submodule update --init --recursive'
    check_call(cmd, shell=True)

    # update mahimahi source line
    cmd = 'sudo add-apt-repository -y ppa:keithw/mahimahi'
    check_call(cmd, shell=True)

    # update package listings
    cmd = 'sudo apt-get update'
    check_call(cmd, shell=True)

    # install required packages
    cmd = 'sudo apt-get -y install mahimahi ntp ntpdate texlive python-pip'
    check_call(cmd, shell=True)

    cmd = 'sudo pip install matplotlib numpy tabulate pyyaml colorama'
    check_call(cmd, shell=True)

    # install pantheon tunnel
    deps = ('debhelper autotools-dev dh-autoreconf iptables pkg-config '
            'iproute2 iptables iproute2')
    cmd = 'sudo apt-get -y install ' + deps
    check_call(cmd, shell=True)

    project_root_dir = path.dirname(path.abspath(__file__))
    tunnel_repo = path.join(project_root_dir, 'third_party', 'pantheon-tunnel')
    cmd = './autogen.sh && ./configure && make -j2 && sudo make install'
    check_call(cmd, shell=True, cwd=tunnel_repo)


if __name__ == '__main__':
    main()
