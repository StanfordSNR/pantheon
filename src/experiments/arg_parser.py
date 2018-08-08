from os import path
import sys
import yaml
import argparse

import context
from helpers import utils


def verify_schemes(schemes):
    schemes = schemes.split()
    all_schemes = utils.parse_config()['schemes'].keys()

    for cc in schemes:
        if cc not in all_schemes:
            sys.exit('%s is not a scheme included in src/config.yml' % cc)


def parse_setup_system():
    parser = argparse.ArgumentParser()

    parser.add_argument('--enable-ip-forward', action='store_true',
                        help='enable IP forwarding')
    parser.add_argument('--interface',
                        help='interface to disable reverse path filtering')
    parser.add_argument('--qdisc', help='change default qdisc')

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--set-rmem', action='store_true',
        help='set socket receive buffer sizes to Pantheon\'s required ones')
    group.add_argument(
        '--reset-rmem', action='store_true',
        help='set socket receive buffer sizes to Linux default ones')
    group.add_argument(
        '--set-all-mem', action='store_true',
        help='set socket send and receive buffer sizes')
    group.add_argument(
        '--reset-all-mem', action='store_true',
        help='set socket send and receive buffer sizes to Linux default ones')

    args = parser.parse_args()
    return args


def parse_setup():
    parser = argparse.ArgumentParser(
        description='by default, run "setup_after_reboot" on specified '
        'schemes and system-wide setup required every time after reboot')

    # schemes related
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--all', action='store_true',
                       help='set up all schemes specified in src/config.yml')
    group.add_argument('--schemes', metavar='"SCHEME1 SCHEME2..."',
                       help='set up a space-separated list of schemes')

    parser.add_argument('--install-deps', action='store_true',
                        help='install dependencies of schemes')
    parser.add_argument('--setup', action='store_true',
                        help='run "setup" on each scheme')

    args = parser.parse_args()
    if args.schemes is not None:
        verify_schemes(args.schemes)

    if args.install_deps:
        if not args.all and args.schemes is None:
            sys.exit('must specify --all or --schemes '
                     'when --install-deps is given')

        if args.setup:
            sys.exit('cannot perform setup when --install-deps is given')

    return args


def parse_test_shared(local, remote, config_args):
    for mode in [local, remote]:
        if config_args.config_file is None:
            mode.add_argument(
                '-f', '--flows', type=int, default=1,
                help='number of flows (default 1)')
        mode.add_argument(
            '-t', '--runtime', type=int, default=30,
            help='total runtime in seconds (default 30)')
        mode.add_argument(
            '--interval', type=int, default=0,
            help='interval in seconds between two flows (default 0)')

        if config_args.config_file is None:
            group = mode.add_mutually_exclusive_group(required=True)
            group.add_argument('--all', action='store_true',
                           help='test all schemes specified in src/config.yml')
            group.add_argument('--schemes', metavar='"SCHEME1 SCHEME2..."',
                               help='test a space-separated list of schemes')

        mode.add_argument('--run-times', metavar='TIMES', type=int, default=1,
                          help='run times of each scheme (default 1)')
        mode.add_argument('--start-run-id', metavar='ID', type=int, default=1,
                          help='run ID to start with')
        mode.add_argument('--random-order', action='store_true',
                          help='test schemes in random order')
        mode.add_argument(
            '--data-dir', metavar='DIR',
            default=path.join(context.src_dir, 'experiments', 'data'),
            help='directory to save all test logs, graphs, '
            'metadata, and report (default pantheon/src/experiments/data)')
        mode.add_argument(
            '--pkill-cleanup', action='store_true', help='clean up using pkill'
            ' (send SIGKILL when necessary) if there were errors during tests')


def parse_test_local(local):
    local.add_argument(
        '--uplink-trace', metavar='TRACE',
        default=path.join(context.src_dir, 'experiments', '12mbps.trace'),
        help='uplink trace (from sender to receiver) to pass to mm-link '
        '(default pantheon/test/12mbps.trace)')
    local.add_argument(
        '--downlink-trace', metavar='TRACE',
        default=path.join(context.src_dir, 'experiments', '12mbps.trace'),
        help='downlink trace (from receiver to sender) to pass to mm-link '
        '(default pantheon/test/12mbps.trace)')
    local.add_argument(
        '--prepend-mm-cmds', metavar='"CMD1 CMD2..."',
        help='mahimahi shells to run outside of mm-link')
    local.add_argument(
        '--append-mm-cmds', metavar='"CMD1 CMD2..."',
        help='mahimahi shells to run inside of mm-link')
    local.add_argument(
        '--extra-mm-link-args', metavar='"ARG1 ARG2..."',
        help='extra arguments to pass to mm-link when running locally. Note '
        'that uplink (downlink) always represents the link from sender to '
        'receiver (from receiver to sender)')


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
        '--local-addr', metavar='IP',
        help='local IP address that can be reached from remote host, '
        'required if "--tunnel-server local" is given')
    remote.add_argument(
        '--local-if', metavar='INTERFACE',
        help='local interface to run pantheon tunnel on')
    remote.add_argument(
        '--remote-if', metavar='INTERFACE',
        help='remote interface to run pantheon tunnel on')
    remote.add_argument(
        '--ntp-addr', metavar='HOST',
        help='address of an NTP server to query clock offset')
    remote.add_argument(
        '--local-desc', metavar='DESC',
        help='extra description of the local side')
    remote.add_argument(
        '--remote-desc', metavar='DESC',
        help='extra description of the remote side')


def verify_test_args(args):
    if args.flows == 0:
        prepend = getattr(args, 'prepend_mm_cmds', None)
        append = getattr(args, 'append_mm_cmds', None)
        extra = getattr(args, 'extra_mm_link_args', None)
        if append is not None or prepend is not None or extra is not None:
            sys.exit('Cannot apply --prepend-mm-cmds, --append-mm-cmds or '
                     '--extra-mm-link-args without pantheon tunnels')

    if args.runtime > 60 or args.runtime <= 0:
        sys.exit('runtime cannot be non-positive or greater than 60 s')
    if args.flows < 0:
        sys.exit('flow cannot be negative')
    if args.interval < 0:
        sys.exit('interval cannot be negative')
    if args.flows > 0 and args.interval > 0:
        if (args.flows - 1) * args.interval > args.runtime:
            sys.exit('interval time between flows is too long to be '
                     'fit in runtime')

def parse_test_config(test_config, local, remote):
    # Check config file has atleast a test-name and a description of flows
    if 'test-name' not in test_config:
        sys.exit('Config file must have a test-name argument')
    if 'flows' not in test_config:
        sys.exit('Config file must specify flows')

    defaults = {}
    defaults.update(**test_config)
    defaults['schemes'] = None
    defaults['all'] = False
    defaults['flows'] = len(test_config['flows'])
    defaults['test_config'] = test_config

    local.set_defaults(**defaults)
    remote.set_defaults(**defaults)


def parse_test():
    # Load configuration file before parsing other command line options
    # Command line options will override options in config file
    config_parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False)
    config_parser.add_argument('-c','--config_file', metavar='CONFIG',
                               help='path to configuration file. '
                               'command line arguments will override options '
                               'in config file. ')
    config_args, remaining_argv = config_parser.parse_known_args()

    parser = argparse.ArgumentParser(
        description='perform congestion control tests',
        parents=[config_parser])

    subparsers = parser.add_subparsers(dest='mode')
    local = subparsers.add_parser(
        'local', help='test schemes locally in mahimahi emulated networks')
    remote = subparsers.add_parser(
        'remote', help='test schemes between local and remote in '
        'real-life networks')
    remote.add_argument(
        'remote_path', metavar='HOST:PANTHEON-DIR',
        help='HOST ([user@]IP) and PANTHEON-DIR (remote pantheon directory)')

    parse_test_shared(local, remote, config_args)
    parse_test_local(local)
    parse_test_remote(remote)

    # Make settings in config file the defaults
    test_config = None
    if config_args.config_file is not None:
        with open(config_args.config_file) as f:
            test_config = yaml.safe_load(f)
        parse_test_config(test_config, local, remote)

    args = parser.parse_args(remaining_argv)
    if args.schemes is not None:
        verify_schemes(args.schemes)
        args.test_config = None
    elif not args.all:
        assert(test_config is not None)
        schemes = ' '.join([flow['scheme'] for flow in test_config['flows']])
        verify_schemes(schemes)

    verify_test_args(args)
    utils.make_sure_dir_exists(args.data_dir)

    return args
