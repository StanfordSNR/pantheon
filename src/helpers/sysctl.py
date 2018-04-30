import sys

import context
from helpers import utils
from subprocess_wrappers import call, check_output


def get_kernel_attr(sh_cmd, ssh_cmd=None, debug=True):
    if ssh_cmd is not None:
        kernel_attr = check_output(ssh_cmd + [sh_cmd])
    else:
        kernel_attr = check_output(sh_cmd, shell=True)

    if debug:
        is_local = 'local' if ssh_cmd is None else 'remote'
        sys.stderr.write('Got %s %s' % (is_local, kernel_attr))

    kernel_attr = kernel_attr.split('=')[-1].strip()
    return kernel_attr


def set_kernel_attr(sh_cmd, ssh_cmd=None, debug=True):
    if ssh_cmd is not None:
        res = call(ssh_cmd + [sh_cmd])
    else:
        res = call(sh_cmd, shell=True)

    if debug:
        is_local = 'local' if ssh_cmd is None else 'remote'

        items = sh_cmd.split('=')
        attr = items[0].split()[-1].strip()
        val = items[1].strip()

        if res != 0:
            sys.stderr.write('Failed: %s %s to %s\n' % (is_local, attr, val))
        else:
            sys.stderr.write('Set %s %s to %s\n' % (is_local, attr, val))


def get_default_qdisc(ssh_cmd=None, debug=True):
    sh_cmd = 'sysctl net.core.default_qdisc'
    local_qdisc = get_kernel_attr(sh_cmd, debug=debug)

    if ssh_cmd is not None:
        remote_qdisc = get_kernel_attr(sh_cmd, ssh_cmd, debug)
        if local_qdisc != remote_qdisc:
            sys.exit('default_qdisc differs on local and remote sides')

    return local_qdisc


def set_default_qdisc(qdisc, ssh_cmd=None, debug=True):
    sh_cmd = 'sudo sysctl -w net.core.default_qdisc=%s' % qdisc
    set_kernel_attr(sh_cmd, ssh_cmd, debug)


def check_default_qdisc(cc):
    config = utils.parse_config()
    cc_config = config['schemes'][cc]
    kernel_qdisc = get_default_qdisc(debug=False)

    if 'qdisc' in cc_config:
        required_qdisc = cc_config['qdisc']
    else:
        required_qdisc = config['kernel_attrs']['default_qdisc']

    if kernel_qdisc != required_qdisc:
        sys.exit('Your default packet scheduler is "%s" currently. Please run '
                 '"sudo sysctl -w net.core.default_qdisc=%s" to use the '
                 'appropriate queueing discipline for %s to work, and change '
                 'it back after testing.'
                 % (kernel_qdisc, required_qdisc, cc_config['friendly_name']))
