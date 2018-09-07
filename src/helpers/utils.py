import os
from os import path
import sys
import socket
import signal
import errno
import json
import yaml
import subprocess
from datetime import datetime

import context
from subprocess_wrappers import check_call, check_output, call


def get_open_port():
    sock = socket.socket(socket.AF_INET)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    return str(port)


def make_sure_dir_exists(d):
    try:
        os.makedirs(d)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


tmp_dir = path.join(context.base_dir, 'tmp')
make_sure_dir_exists(tmp_dir)


def parse_config():
    with open(path.join(context.src_dir, 'config.yml')) as config:
        return yaml.load(config)


def update_submodules():
    cmd = 'git submodule update --init --recursive'
    check_call(cmd, shell=True)


class TimeoutError(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutError()


def utc_time():
    return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')


def kill_proc_group(proc, signum=signal.SIGTERM):
    if not proc:
        return

    try:
        sys.stderr.write('kill_proc_group: killed process group with pgid %s\n'
                         % os.getpgid(proc.pid))
        os.killpg(os.getpgid(proc.pid), signum)
    except OSError as exception:
        sys.stderr.write('kill_proc_group: %s\n' % exception)


def apply_patch(patch_name, repo_dir):
    patch = path.join(context.src_dir, 'wrappers', 'patches', patch_name)

    if call(['git', 'apply', patch], cwd=repo_dir) != 0:
        sys.stderr.write('patch apply failed but assuming things okay '
                         '(patch applied previously?)\n')


def load_test_metadata(metadata_path):
    with open(metadata_path) as metadata:
        return json.load(metadata)


def verify_schemes_with_meta(schemes, meta):
    schemes_config = parse_config()['schemes']

    all_schemes = meta['cc_schemes']
    if schemes is None:
        cc_schemes = all_schemes
    else:
        cc_schemes = schemes.split()

    for cc in cc_schemes:
        if cc not in all_schemes:
            sys.exit('%s is not a scheme included in '
                     'pantheon_metadata.json' % cc)
        if cc not in schemes_config:
            sys.exit('%s is not a scheme included in src/config.yml' % cc)

    return cc_schemes


def who_runs_first(cc):
    cc_src = path.join(context.src_dir, 'wrappers', cc + '.py')

    cmd = [cc_src, 'run_first']
    run_first = check_output(cmd).strip()

    if run_first == 'receiver':
        run_second = 'sender'
    elif run_first == 'sender':
        run_second = 'receiver'
    else:
        sys.exit('Must specify "receiver" or "sender" runs first')

    return run_first, run_second


def parse_remote_path(remote_path, cc=None):
    ret = {}

    ret['host_addr'], ret['base_dir'] = remote_path.rsplit(':', 1)
    ret['src_dir'] = path.join(ret['base_dir'], 'src')
    ret['tmp_dir'] = path.join(ret['base_dir'], 'tmp')
    ret['ip'] = ret['host_addr'].split('@')[-1]
    ret['ssh_cmd'] = ['ssh', ret['host_addr']]
    ret['tunnel_manager'] = path.join(
        ret['src_dir'], 'experiments', 'tunnel_manager.py')

    if cc is not None:
        ret['cc_src'] = path.join(ret['src_dir'], 'wrappers', cc + '.py')

    return ret


def query_clock_offset(ntp_addr, ssh_cmd):
    local_clock_offset = None
    remote_clock_offset = None

    ntp_cmds = {}
    ntpdate_cmd = ['ntpdate', '-t', '5', '-quv', ntp_addr]

    ntp_cmds['local'] = ntpdate_cmd
    ntp_cmds['remote'] = ssh_cmd + ntpdate_cmd

    for side in ['local', 'remote']:
        cmd = ntp_cmds[side]

        fail = True
        for _ in xrange(3):
            try:
                offset = check_output(cmd)
                sys.stderr.write(offset)

                offset = offset.rsplit(' ', 2)[-2]
                offset = str(float(offset) * 1000)
            except subprocess.CalledProcessError:
                sys.stderr.write('Failed to get clock offset\n')
            except ValueError:
                sys.stderr.write('Cannot convert clock offset to float\n')
            else:
                if side == 'local':
                    local_clock_offset = offset
                else:
                    remote_clock_offset = offset

                fail = False
                break

        if fail:
            sys.stderr.write('Failed after 3 queries to NTP server\n')

    return local_clock_offset, remote_clock_offset


def get_git_summary(mode='local', remote_path=None):
    git_summary_src = path.join(context.src_dir, 'experiments',
                                'git_summary.sh')
    local_git_summary = check_output(git_summary_src, cwd=context.base_dir)

    if mode == 'remote':
        r = parse_remote_path(remote_path)

        git_summary_src = path.join(
            r['src_dir'], 'experiments', 'git_summary.sh')
        ssh_cmd = 'cd %s; %s' % (r['base_dir'], git_summary_src)
        ssh_cmd = ' '.join(r['ssh_cmd']) + ' "%s"' % ssh_cmd

        remote_git_summary = check_output(ssh_cmd, shell=True)

        if local_git_summary != remote_git_summary:
            sys.stderr.write(
                '--- local git summary ---\n%s\n' % local_git_summary)
            sys.stderr.write(
                '--- remote git summary ---\n%s\n' % remote_git_summary)
            sys.exit('Repository differed between local and remote sides')

    return local_git_summary


def save_test_metadata(meta, metadata_path):
    meta.pop('all')
    meta.pop('schemes')
    meta.pop('data_dir')
    meta.pop('pkill_cleanup')

    # use list in case meta.keys() returns an iterator in Python 3
    for key in list(meta.keys()):
        if meta[key] is None:
            meta.pop(key)

    if 'uplink_trace' in meta:
        meta['uplink_trace'] = path.basename(meta['uplink_trace'])
    if 'downlink_trace' in meta:
        meta['downlink_trace'] = path.basename(meta['downlink_trace'])

    with open(metadata_path, 'w') as metadata_fh:
        json.dump(meta, metadata_fh, sort_keys=True, indent=4,
                  separators=(',', ': '))


def get_sys_info():
    sys_info = ''
    sys_info += check_output(['uname', '-sr'])
    sys_info += check_output(['sysctl', 'net.core.default_qdisc'])
    sys_info += check_output(['sysctl', 'net.core.rmem_default'])
    sys_info += check_output(['sysctl', 'net.core.rmem_max'])
    sys_info += check_output(['sysctl', 'net.core.wmem_default'])
    sys_info += check_output(['sysctl', 'net.core.wmem_max'])
    sys_info += check_output(['sysctl', 'net.ipv4.tcp_rmem'])
    sys_info += check_output(['sysctl', 'net.ipv4.tcp_wmem'])
    return sys_info
