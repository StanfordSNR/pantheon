#!/usr/bin/env python

from os import path
from helpers.helpers import parse_arguments, check_call, update_submodules


def install_deps():
    # update mahimahi source line
    cmd = 'sudo add-apt-repository -y ppa:keithw/mahimahi'
    check_call(cmd, shell=True)

    # update package listings
    cmd = 'sudo apt-get update'
    check_call(cmd, shell=True)

    cmd = 'sudo apt-get -y install mahimahi ntp ntpdate texlive python-pip'
    check_call(cmd, shell=True)

    cmd = 'pip install matplotlib numpy tabulate pyyaml'
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


def setup(args):
    update_submodules()

    # install dependencies
    install_deps()

    if args.interface is not None:
        # disable reverse path filtering
        rpf = ' /proc/sys/net/ipv4/conf/%s/rp_filter'
        cmd = 'echo 0 | sudo tee' + rpf % 'all' + rpf % args.interface
        check_call(cmd, shell=True)


def main():
    args = parse_arguments(path.abspath(__file__))
    setup(args)


if __name__ == '__main__':
    main()
