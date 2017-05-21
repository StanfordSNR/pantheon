import argparse


def parse_setup():
    parser = argparse.ArgumentParser(
        description='by default, run "setup_after_reboot" on specified '
        'schemes and system-wide setup required every time after reboot')

    # system-wide
    parser.add_argument('--interface',
                        help='interface to disable reverse path filtering')

    # schemes related
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--all', action='store_true',
                       help='set up all schemes specified in config.yml')
    group.add_argument('--schemes', metavar='"SCHEME1 SCHEME2..."',
                       help='set up a space-separated list of schemes')

    parser.add_argument('--install-deps', action='store_true',
                        help='install dependencies of schemes')
    parser.add_argument('--setup', action='store_true',
                        help='run "setup" on each scheme')

    args = parser.parse_args()
    return args


def parse_test_shared(local, remote):
    for mode in [local, remote]:
        mode.add_argument(
            '-f', '--flows', type=int, default=1,
            help='number of flows (default 1)')
        mode.add_argument(
            '-t', '--runtime', type=int, default=30,
            help='total runtime in seconds (default 30)')
        mode.add_argument(
            '--interval', type=int, default=0,
            help='interval in seconds between two flows (default 0)')

        group = mode.add_mutually_exclusive_group(required=True)
        group.add_argument('--all', action='store_true',
                           help='test all schemes specified in config.yml')
        group.add_argument('--schemes', metavar='"SCHEME1 SCHEME2..."',
                           help='test a space-separated list of schemes')

        mode.add_argument('--run-times', metavar='TIMES', type=int, default=1,
                          help='run times of each scheme (default 1)')
        mode.add_argument('--random-order', action='store_true',
                          help='test schemes in random order')


def parse_test_local(local):
    local.add_argument(
        '--uplink-trace', metavar='TRACE', default='12mbps.trace',
        help='uplink trace (from sender to receiver) to pass to mm-link '
        '(default 12mbps.trace)')
    local.add_argument(
        '--downlink-trace', metavar='TRACE', default='12mbps.trace',
        help='downlink trace (from receiver to sender) to pass to mm-link '
        '(default 12mbps.trace)')
    local.add_argument(
        '--prepend-mm-cmds', metavar='"CMD1 CMD2..."',
        help='mahimahi shells to run outside of mm-link')
    local.add_argument(
        '--append-mm-cmds', metavar='"CMD1 CMD2..."',
        help='mahimahi shells to run inside of mm-link')
    local.add_argument(
        '--extra-mm-link-args', metavar='"ARG1 ARG2..."',
        help='extra arguments to pass to mm-link when running locally')


def parse_test_remote(remote):
    remote.add_argument(
        '--sender', choices=['local', 'remote'], default='local',
        action='store', dest='sender_side',
        help='the side to be data sender (default local)')
    remote.add_argument(
        '--tunnel-server', choices=['local', 'remote'], default='remote',
        action='store', dest='server_side',
        help='the side to run pantheon tunnel server on (default remote)')
    remote.add_argument(
        '--local-addr', metavar='ADDR',
        help='local address that can be reached from remote host, '
        'required if "--tunnel-server local" is given')
    remote.add_argument(
        '--local-if', metavar='INTERFACE',
        help='local interface to run pantheon tunnel on')
    remote.add_argument(
        '--remote-if', metavar='INTERFACE',
        help='remote interface to run pantheon tunnel on')
    remote.add_argument(
        '--ntp-addr', metavar='ADDR',
        help='address of an NTP server to query clock offset')
    remote.add_argument(
        '--local-desc', metavar='DESC',
        help='extra description of the local side')
    remote.add_argument(
        '--remote-desc', metavar='DESC',
        help='extra description of the remote side')


def parse_test():
    parser = argparse.ArgumentParser(
        description='perform congestion control tests')
    subparsers = parser.add_subparsers(dest='mode')

    local = subparsers.add_parser(
        'local', help='test schemes locally in mahimahi emulated networks')
    remote = subparsers.add_parser(
        'remote', help='test schemes between local and remote in '
        'real-life networks')
    remote.add_argument(
        'remote_path', metavar='HOSTADDR:PANTHEON-DIR',
        help='HOSTADDR ([user@]hostname) and PANTHEON-DIR (remote pantheon '
        'directory)')

    parse_test_shared(local, remote)
    parse_test_local(local)
    parse_test_remote(remote)

    args = parser.parse_args()
    return args


def parse_arguments(filename):
    if filename == 'setup.py':
        return parse_setup()
    elif filename == 'test.py':
        return parse_test()
