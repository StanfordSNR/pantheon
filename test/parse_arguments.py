import argparse
import sys


def build_arg_dict():
    arg_dict = {}

    arg_dict['-r'] = {
        'metavar': 'REMOTE:PANTHEON-DIR',
        'action': 'store',
        'dest': 'remote',
        'help': 'REMOTE: [user@]hostname; PANTHEON-DIR: must be an '
                'absolute path (can be prefixed by ~) to the pantheon root '
                'directory on the remote side',
    }

    arg_dict['-f'] = {
        'metavar': 'FLOWS',
        'action': 'store',
        'dest': 'flows',
        'type': int,
        'default': 1,
        'help': 'number of flows (default 1)',
    }

    arg_dict['-t'] = {
        'metavar': 'RUNTIME',
        'action': 'store',
        'dest': 'runtime',
        'type': int,
        'default': 30,
        'help': 'total runtime in seconds (default 30)',
    }

    arg_dict['--interval'] = {
        'metavar': 'INTERVAL',
        'action': 'store',
        'dest': 'interval',
        'type': int,
        'default': 0,
        'help': 'interval in seconds between two flows (default 0)',
    }

    arg_dict['--tunnel-server'] = {
        'choices': ['local', 'remote'],
        'action': 'store',
        'dest': 'server_side',
        'default': 'remote',
        'help': 'the side to run mm-tunnelserver on (default remote)',
    }

    arg_dict['--local-addr'] = {
        'metavar': 'IP-ADDR',
        'action': 'store',
        'dest': 'local_addr',
        'help': 'local IP address; if "--tunnel-server local" is '
                'given, the remote side must be able to reach this address',
    }

    arg_dict['--sender-side'] = {
        'choices': ['local', 'remote'],
        'action': 'store',
        'dest': 'sender_side',
        'default': 'local',
        'help': 'the side to be data sender (default local)',
    }

    arg_dict['--local-interface'] = {
        'metavar': 'INTERFACE',
        'action': 'store',
        'dest': 'local_if',
        'help': 'local interface to run tunnel on',
    }

    arg_dict['--remote-interface'] = {
        'metavar': 'INTERFACE',
        'action': 'store',
        'dest': 'remote_if',
        'help': 'remote interface to run tunnel on',
    }

    arg_dict['--local-info'] = {
        'metavar': 'INFO',
        'action': 'store',
        'dest': 'local_info',
        'help': 'extra information about the local side',
    }

    arg_dict['--remote-info'] = {
        'metavar': 'INFO',
        'action': 'store',
        'dest': 'remote_info',
        'help': 'extra information about the remote side',
    }

    arg_dict['--metadata-file'] = {
        'metavar': 'FILENAME',
        'action': 'store',
        'dest': 'metadata_file',
        'help': 'file containing metadata to be included in pantheon report',
    }

    arg_dict['--run-only'] = {
        'choices': ['setup', 'test'],
        'action': 'store',
        'dest': 'run_only',
        'help': 'run setup or test only',
    }

    arg_dict['--random-order'] = {
        'action': 'store_true',
        'dest': 'random_order',
        'help': 'test congestion control schemes in random order',
    }

    arg_dict['cc'] = {
        'metavar': 'congestion-control',
        'help': 'a congestion control scheme in default_tcp, koho_cc, ledbat, '
                'pcc, quic, scream, sprout, vegas, verus, webrtc',
    }

    arg_dict['cc_schemes'] = {
        'metavar': 'congestion-control',
        'nargs': '+',
        'help': 'congestion control schemes',
    }

    return arg_dict


def add_arg_list(parser, arg_dict, arg_list):
    for arg in arg_list:
        assert arg in arg_dict, '%s has not been defined' % arg
        parser.add_argument(arg, **arg_dict[arg])


def validate_args(args):
    remote = getattr(args, 'remote', None)
    flows = getattr(args, 'flows', None)
    runtime = getattr(args, 'runtime', None)
    interval = getattr(args, 'interval', None)
    server_side = getattr(args, 'server_side', None)
    local_addr = getattr(args, 'local_addr', None)
    remote_if = getattr(args, 'remote_if', None)

    if remote_if:
        assert remote, '--remote-interface must run along with -r'

    if remote:
        assert ':' in remote, '-r must be followed by [user@]hostname:dir'
        if flows:
            assert flows >= 1, 'remote test must run at least one flow'

    if runtime:
        assert runtime <= 60, 'runtime cannot be greater than 60 seconds'
        if flows and interval:
            assert (flows - 1) * interval < runtime, (
                'interval time between flows is too long to be fit in runtime')

    if server_side == 'local':
        assert local_addr, (
            'must provide local address that can be reached by the other '
            'side if "--tunnel-server local"')


def parse_arguments(filename):
    parser = argparse.ArgumentParser()
    arg_dict = build_arg_dict()

    if filename == 'setup.py':
        add_arg_list(parser, arg_dict, [
            '-r', '--local-interface', '--remote-interface', 'cc'])
    elif filename == 'test.py':
        add_arg_list(parser, arg_dict, [
            '-r', '-t', '-f', '--interval', '--tunnel-server',
            '--local-addr', '--sender-side', '--local-interface',
            '--remote-interface', 'cc'])
    elif filename == 'combine_reports.py':
        add_arg_list(parser, arg_dict, ['--metadata-file', 'cc_schemes'])
    elif filename == 'run.py':
        add_arg_list(parser, arg_dict, [
            '-r', '-t', '-f', '--interval', '--tunnel-server',
            '--local-addr', '--sender-side', '--local-interface',
            '--remote-interface', '--local-info', '--remote-info',
            '--run-only', '--random-order'])

    args = parser.parse_args()
    validate_args(args)

    return args
