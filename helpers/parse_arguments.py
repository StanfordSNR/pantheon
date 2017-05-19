import sys
import argparse
from os import path
import yaml
import project_root


def build_arg_dict(cc_schemes):
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
        'help': 'run ID of the test (default 1)',
    }

    arg_dict['--run-times'] = {
        'metavar': 'N',
        'type': int,
        'default': 1,
        'help': 'run times of each test (default 1)',
    }

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

    arg_dict['--datalink-trace'] = {
        'metavar': 'TRACE',
        'default': '12mbps.trace',
        'help': 'datalink trace (from sender to receiver) to pass in mm-link '
                'when running locally (default 12mbps.trace)',
    }

    arg_dict['--acklink-trace'] = {
        'metavar': 'TRACE',
        'default': '12mbps.trace',
        'help': 'acklink trace (from receiver to sender) to pass in mm-link '
                'when running locally (default 12mbps.trace)',
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


def validate_args(args, cc_schemes_list):
    cc = getattr(args, 'cc', None)
    remote = getattr(args, 'remote', None)
    flows = getattr(args, 'flows', None)
    runtime = getattr(args, 'runtime', None)
    interval = getattr(args, 'interval', None)
    run_id = getattr(args, 'run_id', None)
    server_side = getattr(args, 'server_side', None)
    local_addr = getattr(args, 'local_addr', None)
    sender_side = getattr(args, 'sender_side', None)
    remote_if = getattr(args, 'remote_if', None)
    remote_info = getattr(args, 'remote_info', None)
    prepend_mm_cmds = getattr(args, 'prepend_mm_cmds', None)
    append_mm_cmds = getattr(args, 'append_mm_cmds', None)
    extra_mm_link_args = getattr(args, 'extra_mm_link_args', None)

    if cc is not None:
        if cc not in cc_schemes_list:
            sys.exit('%s is not listed in src/config.yml' % cc)

    if remote_if is not None:
        if remote is None:
            sys.exit('--remote-interface must run along with -r')

    if remote_info is not None:
        if remote is None:
            sys.exit('--remote-info must run along with -r')

    if remote is not None:
        if ':' not in remote:
            sys.exit('-r must be followed by [user@]hostname:dir')

        if flows < 1:
            sys.exit('remote test must run at least one flow')

    if runtime is not None:
        if runtime > 60 or runtime <= 0:
            sys.exit('runtime cannot be non-positive or greater than 60 s')

    if flows is not None and flows < 0:
        sys.exit('flow cannot be negative')

    if interval is not None and interval < 0:
        sys.exit('interval cannot be negative')

    if flows is not None and interval is not None:
        if flows > 0 and interval > 0:
            if (flows - 1) * interval > runtime:
                sys.exit('interval time between flows is too long to be '
                         'fit in runtime')

    if run_id is not None and run_id <= 0:
        sys.exit('run_id must be positive')

    if server_side == 'local':
        if local_addr is None:
            sys.exit('must provide local address that can be reached by the '
                     'other side if "--tunnel-server local"')

    if server_side == 'local' or sender_side == 'remote':
        if remote is None:
            sys.exit('local test can only run tunnel server and sender '
                     'inside mm-link')

    if remote is not None:
        if prepend_mm_cmds is not None:
            sys.exit('--prepend-mm-cmds can\'t be run with -r')

        if append_mm_cmds is not None:
            sys.exit('--append-mm-cmds can\'t be run with -r')

        if extra_mm_link_args is not None:
            sys.exit('--extra-mm-link-args can\'t be run with -r')


def parse_arguments(file_path):
    with open(path.join(project_root.DIR, 'src', 'config.yml')) as config:
        cfg = yaml.load(config)
    cc_schemes_list = cfg.keys()
    cc_schemes = ' '.join(cc_schemes_list)

    parser = argparse.ArgumentParser()
    arg_dict = build_arg_dict(cc_schemes)

    test_dir = path.join(project_root.DIR, 'test')
    analyze_dir = path.join(project_root.DIR, 'analyze')

    if file_path == path.join(test_dir, 'setup.py'):
        add_arg_list(parser, arg_dict, [
            '--install-deps', '--build', 'cc_schemes'])
    elif file_path == path.join(test_dir, 'test.py'):
        add_arg_list(parser, arg_dict, [
            '-r', '-t', '-f', '--interval', '--tunnel-server',
            '--local-addr', '--sender-side', '--local-if',
            '--remote-if', '--run-id', '--datalink-trace',
            '--acklink-trace', '--prepend-mm-cmds', '--append-mm-cmds',
            '--extra-mm-link-args', '--ntp-addr', 'cc'])
    elif file_path == path.join(test_dir, 'run.py'):
        add_arg_list(parser, arg_dict, [
            '-r', '-t', '-f', '--interval', '--tunnel-server',
            '--local-addr', '--sender-side', '--local-if',
            '--remote-if', '--local-info', '--remote-info',
            '--run-only', '--random-order', '--run-times', '--ntp-addr',
            '--datalink-trace', '--acklink-trace', '--prepend-mm-cmds',
            '--append-mm-cmds', '--extra-mm-link-args', '--schemes'])
    elif file_path == path.join(analyze_dir, 'plot_summary.py'):
        add_arg_list(parser, arg_dict,
                     ['--data-dir', '--include-acklink', '--no-plots',
                      '--analyze-schemes'])
    elif file_path == path.join(analyze_dir, 'generate_report.py'):
        add_arg_list(parser, arg_dict, ['--data-dir', '--include-acklink',
                                        '--analyze-schemes'])
    elif file_path == path.join(analyze_dir, 'full_experiment_plot.py'):
        add_arg_list(parser, arg_dict, ['--ms-per-bin', '--data-dir'])
    elif file_path == path.join(analyze_dir, 'analyze.py'):
        add_arg_list(parser, arg_dict, [
            '--s3-link', '--s3-dir-prefix', '--data-dir', '--no-pre-setup',
            '--include-acklink', '--analyze-schemes'])

    args = parser.parse_args()
    validate_args(args, cc_schemes_list)

    return args


def parse_remote(remote, cc=None):
    ret = {}

    ret['addr'], ret['pantheon_dir'] = remote.split(':')
    ret['ip'] = ret['addr'].split('@')[-1]
    ret['ssh_cmd'] = ['ssh', ret['addr']]

    ret['src_dir'] = path.join(ret['pantheon_dir'], 'src')
    ret['test_dir'] = path.join(ret['pantheon_dir'], 'test')
    ret['install_deps'] = path.join(ret['pantheon_dir'], 'install_deps.py')

    ret['setup'] = path.join(ret['test_dir'], 'setup.py')
    ret['tunnel_manager'] = path.join(ret['test_dir'], 'tunnel_manager.py')

    if cc:
        ret['cc_src'] = path.join(ret['src_dir'], cc + '.py')

    return ret
