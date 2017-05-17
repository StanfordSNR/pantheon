import argparse
from os import path
import yaml
import project_root


def build_arg_dict():
    arg_dict = {}

    arg_dict['-r'] = {
        'metavar': 'HOSTADDR:PANTHEON-DIR',
        'action': 'store',
        'dest': 'remote',
        'help': 'HOSTADDR: [user@]IP; '
                'PANTHEON-DIR: pantheon directory on the remote side',
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
        'metavar': 'IP',
        'help': 'local IP address; if "--tunnel-server local" is '
                'given, the remote side must be able to reach this address',
    }

    arg_dict['--ntp-addr'] = {
        'metavar': 'ADDR',
        'help': 'IP address or domain of ntp server '
                'to check clock offset with',
    }

    arg_dict['--sender-side'] = {
        'choices': ['local', 'remote'],
        'default': 'local',
        'help': 'the side to be data sender (default local)',
    }

    arg_dict['--local-if'] = {
        'metavar': 'INTERFACE',
        'action': 'store',
        'dest': 'local_if',
        'help': 'local interface to run tunnel on',
    }

    arg_dict['--remote-if'] = {
        'metavar': 'INTERFACE',
        'action': 'store',
        'dest': 'remote_if',
        'help': 'remote interface to run tunnel on',
    }

    arg_dict['--interface'] = {
        'help': 'interface on which to disable reverse path filtering',
    }

    arg_dict['--local-info'] = {
        'metavar': 'INFO',
        'help': 'extra information about the local side',
    }

    arg_dict['--remote-info'] = {
        'metavar': 'INFO',
        'help': 'extra information about the remote side',
    }

    arg_dict['--install-deps'] = {
        'action': 'store_true',
        'help': 'install dependencies',
    }

    arg_dict['--build'] = {
        'action': 'store_true',
        'help': 'build the scheme',
    }

    arg_dict['--run-only'] = {
        'choices': ['setup', 'test'],
        'help': 'run setup or test only',
    }

    arg_dict['--random-order'] = {
        'action': 'store_true',
        'help': 'test congestion control schemes in random order',
    }

    arg_dict['--run-id'] = {
        'metavar': 'ID',
        'type': int,
        'default': 1,
        'help': 'run ID of the test',
    }

    arg_dict['--run-times'] = {
        'metavar': 'N',
        'type': int,
        'default': 1,
        'help': 'run times of each test (default 1)',
    }

    with open(path.join(project_root.DIR, 'src', 'config.yml')) as config:
        cfg = yaml.load(config)
    cc_schemes = ' '.join(cfg.keys())

    arg_dict['--schemes'] = {
        'metavar': '"SCHEME_1 SCHEME_2..."',
        'default': cc_schemes,
        'help': 'what congestion control schemes to run '
                '(default: \"%s\")' % cc_schemes,
    }

    arg_dict['--analyze-schemes'] = {
        'metavar': '"SCHEME_1 SCHEME_2..."',
        'help': 'what congestion control schemes to analyze '
                '(default: is contents of pantheon_metadata.json',
    }

    arg_dict['--uplink-trace'] = {
        'metavar': 'TRACE',
        'default': '12mbps.trace',
        'help': 'uplink trace to pass to mm-link when running locally '
                '(default 12mbps.trace)',
    }

    arg_dict['--downlink-trace'] = {
        'metavar': 'TRACE',
        'default': '12mbps.trace',
        'help': 'downlink trace to pass to mm-link when running locally '
                '(default 12mbps.trace)',
    }

    arg_dict['--prepend-mm-cmds'] = {
        'metavar': '"CMD1 CMD2..."',
        'help': 'mahimahi shells to run outside of mm-link when running'
                ' locally',
    }

    arg_dict['--append-mm-cmds'] = {
        'metavar': '"CMD1 CMD2..."',
        'help': 'mahimahi shells to run inside of mm-link when running'
                ' locally',
    }

    arg_dict['--extra-mm-link-args'] = {
        'metavar': '"ARG1 ARG2..."',
        'help': 'extra arguments to pass to mm-link when running locally',
    }

    arg_dict['--ms-per-bin'] = {
        'metavar': 'MS',
        'type': int,
        'default': 1000,
        'help': 'ms per bin',
    }

    arg_dict['--data-dir'] = {
        'metavar': 'DIR',
        'default': '.',
        'help': 'directory containing logs for analysis (default .)',
    }

    arg_dict['--no-plots'] = {
        'action': 'store_true',
        'help': 'don\'t output plots',
    }

    arg_dict['--s3-link'] = {
        'metavar': 'URL',
        'help': 'URL to download logs from S3',
    }

    arg_dict['--s3-dir-prefix'] = {
        'metavar': 'DIR',
        'default': '.',
        'help': 'directory to save downloaded logs from S3 (default .)',
    }

    arg_dict['cc'] = {
        'metavar': 'congestion-control',
        'help': 'a congestion control scheme',
    }

    arg_dict['cc_schemes'] = {
        'metavar': 'congestion-control',
        'nargs': '+',
        'help': 'congestion control schemes',
    }

    arg_dict['--include-acklink'] = {
        'action': 'store_true',
        'help': 'include acklink analysis',
    }

    arg_dict['--no-pre-setup'] = {
        'action': 'store_true',
        'help': 'skip pre setup',
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
    sender_side = getattr(args, 'sender_side', None)
    remote_if = getattr(args, 'remote_if', None)
    remote_info = getattr(args, 'remote_info', None)
    prepend_mm_cmds = getattr(args, 'prepend_mm_cmds', None)
    append_mm_cmds = getattr(args, 'append_mm_cmds', None)
    extra_mm_link_args = getattr(args, 'extra_mm_link_args', None)

    if remote_if:
        assert remote, '--remote-interface must run along with -r'

    if remote_info:
        assert remote, '--remote-info must run along with -r'

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

    if server_side == 'local' or sender_side == 'remote':
        assert remote, (
            'local test can only run tunnel server and sender inside mm-link')

    if remote:
        assert not prepend_mm_cmds, '--prepend-mm-cmds can\'t be run with -r'
        assert not append_mm_cmds, '--append-mm-cmds can\'t be run with -r'
        assert not extra_mm_link_args, (
            '--extra-mm-link-args can\'t be run with -r')


def parse_arguments(file_path):
    parser = argparse.ArgumentParser()
    arg_dict = build_arg_dict()

    test_dir = path.join(project_root.DIR, 'test')

    if file_path == path.join(project_root.DIR, 'install_deps.py'):
        add_arg_list(parser, arg_dict, ['--interface'])
    elif file_path == path.join(test_dir, 'setup.py'):
        add_arg_list(parser, arg_dict, [
            '--install-deps', '--build', 'cc_schemes'])
    elif file_path == 'test.py':
        add_arg_list(parser, arg_dict, [
            '-r', '-t', '-f', '--interval', '--tunnel-server',
            '--local-addr', '--sender-side', '--local-if',
            '--remote-if', '--run-id', '--uplink-trace',
            '--downlink-trace', '--prepend-mm-cmds', '--append-mm-cmds',
            '--extra-mm-link-args', '--ntp-addr', 'cc'])
    elif file_path == 'plot_summary.py':
        add_arg_list(parser, arg_dict,
                     ['--data-dir', '--include-acklink', '--no-plots',
                      '--analyze-schemes'])
    elif file_path == 'generate_report.py':
        add_arg_list(parser, arg_dict, ['--data-dir', '--include-acklink',
                                        '--analyze-schemes'])
    elif file_path == 'full_experiment_plot.py':
        add_arg_list(parser, arg_dict, ['--ms-per-bin', '--data-dir'])
    elif file_path == 'analyze.py':
        add_arg_list(parser, arg_dict, [
            '--s3-link', '--s3-dir-prefix', '--data-dir', '--no-pre-setup',
            '--include-acklink', '--analyze-schemes'])
    elif file_path == 'run.py':
        add_arg_list(parser, arg_dict, [
            '-r', '-t', '-f', '--interval', '--tunnel-server',
            '--local-addr', '--sender-side', '--local-if',
            '--remote-if', '--local-info', '--remote-info',
            '--run-only', '--random-order', '--run-times', '--ntp-addr',
            '--uplink-trace', '--downlink-trace', '--prepend-mm-cmds',
            '--append-mm-cmds', '--extra-mm-link-args', '--schemes'])

    args = parser.parse_args()
    validate_args(args)

    return args


def parse_remote(remote, cc=None):
    assert remote, 'error in parse_remote: "remote" must be non-empty'

    ret = {}

    ret['host_addr'], ret['pantheon_dir'] = remote.split(':')
    ret['ip'] = ret['host_addr'].split('@')[-1]
    ret['ssh_cmd'] = ['ssh', ret['host_addr']]

    ret['src_dir'] = path.join(ret['pantheon_dir'], 'src')
    ret['test_dir'] = path.join(ret['pantheon_dir'], 'test')

    ret['pre_setup'] = path.join(ret['test_dir'], 'pre_setup.py')
    ret['setup'] = path.join(ret['test_dir'], 'setup.py')
    ret['tunnel_manager'] = path.join(ret['test_dir'], 'tunnel_manager.py')

    if cc:
        ret['cc_src'] = path.join(ret['src_dir'], cc + '.py')

    return ret
