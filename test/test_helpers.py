import sys
from os import path
import json
import subprocess
import project_root
from helpers.helpers import (check_output, get_kernel_attr, set_kernel_attr)


def who_runs_first(cc):
    cc_src = path.join(project_root.DIR, 'src', cc + '.py')

    cmd = ['python', cc_src, 'run_first']
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

    ret['host_addr'], ret['pantheon_dir'] = remote_path.rsplit(':', 1)
    ret['ip'] = ret['host_addr'].split('@')[-1]
    ret['ssh_cmd'] = ['ssh', ret['host_addr']]
    ret['tunnel_manager'] = path.join(
        ret['pantheon_dir'], 'test', 'tunnel_manager.py')

    if cc is not None:
        ret['cc_src'] = path.join(ret['pantheon_dir'], 'src', cc + '.py')

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
    git_summary_src = path.join(project_root.DIR, 'test', 'git_summary.sh')
    local_git_summary = check_output(git_summary_src, cwd=project_root.DIR)

    if mode == 'remote':
        r = parse_remote_path(remote_path)

        git_summary_src = path.join(
            r['pantheon_dir'], 'test', 'git_summary.sh')
        ssh_cmd = 'cd %s; %s' % (r['pantheon_dir'], git_summary_src)
        ssh_cmd = ' '.join(r['ssh_cmd']) + ' "%s"' % ssh_cmd

        remote_git_summary = check_output(ssh_cmd, shell=True)

        if local_git_summary != remote_git_summary:
            sys.stderr.write(
                '--- local git summary ---\n%s\n' % local_git_summary)
            sys.stderr.write(
                '--- remote git summary ---\n%s\n' % remote_git_summary)
            sys.exit('Repository differed between local and remote sides')

    return local_git_summary


def save_test_metadata(meta, data_dir, git_summary):
    meta.pop('all')
    meta.pop('schemes')
    meta.pop('no_metadata')
    meta.pop('data_dir')
    meta.pop('pkill_cleanup')

    # use list in case meta.keys() returns an iterator in Python 3
    for key in list(meta.keys()):
        if meta[key] is None:
            meta.pop(key)

    meta['git_summary'] = git_summary

    if 'uplink_trace' in meta:
        meta['uplink_trace'] = path.basename(meta['uplink_trace'])
    if 'downlink_trace' in meta:
        meta['downlink_trace'] = path.basename(meta['downlink_trace'])

    metadata_path = path.join(data_dir, 'pantheon_metadata.json')

    with open(metadata_path, 'w') as metadata:
        json.dump(meta, metadata, sort_keys=True, indent=4,
                  separators=(',', ': '))


def get_recv_sock_bufsizes(ssh_cmd=None):
    buf_sizes = {'remote': {}, 'local': {}}

    max_sh_cmd = 'sysctl net.core.rmem_max'
    default_sh_cmd = 'sysctl net.core.rmem_default'
    local_max_bufsize = get_kernel_attr(max_sh_cmd)
    local_default_bufsize = get_kernel_attr(default_sh_cmd)

    buf_sizes['local']['max'] = local_max_bufsize
    buf_sizes['local']['default'] = local_default_bufsize

    if ssh_cmd is not None:
        remote_max_bufsize = get_kernel_attr(max_sh_cmd, ssh_cmd)
        remote_default_bufsize = get_kernel_attr(default_sh_cmd, ssh_cmd)

        buf_sizes['remote']['max'] = remote_max_bufsize
        buf_sizes['remote']['default'] = remote_default_bufsize

    return buf_sizes


def set_recv_sock_bufsizes(bufsizes, ssh_cmd=None):
    max_sh_cmd = 'sudo sysctl -w net.core.rmem_max=%s'
    default_sh_cmd = 'sudo sysctl -w net.core.rmem_default=%s'

    if 'local' in bufsizes:
        set_kernel_attr(max_sh_cmd % bufsizes['local']['max'])
        set_kernel_attr(default_sh_cmd % bufsizes['local']['default'])
    if 'remote' in bufsizes and ssh_cmd is not None:
        set_kernel_attr(max_sh_cmd % bufsizes['remote']['max'], ssh_cmd)
        set_kernel_attr(default_sh_cmd % bufsizes['remote']['default'], ssh_cmd
                        
                        
def set_sock_bufsizes_for_fillp(orgin_udp_men_max, orgin_udp_men_default,orgin_wmen_max):
    if  orgin_udp_men_default >= 268435456 and orgin_udp_men_max >= 268435456 and orgin_wmen_max >= 268435456:
        pass
    else:
        cmd = ['sudo sysctl -w net.ipv4.udp_mem="98304 268435456 268435456"']
        check_call(cmd, shell=True)
        cmd = ['sudo sysctl -w net.core.wmem_max=268435456']
        check_call(cmd, shell=True)

                        
                        
                        
