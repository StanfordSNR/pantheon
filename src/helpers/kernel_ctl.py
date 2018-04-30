import sys

from subprocess_wrappers import call, check_output, check_call


def load_kernel_module(module):
    if call('sudo modprobe ' + module, shell=True) != 0:
        sys.exit('%s kernel module is not available' % module)


def enable_congestion_control(cc):
    cc_list = check_output('sysctl net.ipv4.tcp_allowed_congestion_control',
                           shell=True)
    cc_list = cc_list.split('=')[-1].split()

    # return if cc is already in the allowed congestion control list
    if cc in cc_list:
        return

    cc_list.append(cc)
    check_call('sudo sysctl -w net.ipv4.tcp_allowed_congestion_control="%s"'
               % ' '.join(cc_list), shell=True)


def set_qdisc(qdisc):
    default_qdisc = check_output('sysctl net.core.default_qdisc', shell=True)
    default_qdisc = default_qdisc.split('=')[-1].strip()

    # return if default_qdisc is already qdisc
    if qdisc == default_qdisc:
        return

    check_call('sudo sysctl -w net.core.default_qdisc=%s' % qdisc)
    sys.stderr.write(
        'Warning: changed default qdisc from %s to %s; change it '
        'back before testing other schemes' % (default_qdisc, qdisc))


def enable_ip_forwarding():
    check_call('sudo sysctl -w net.ipv4.ip_forward=1', shell=True)


def disable_rp_filter(interface):
    rpf = 'net.ipv4.conf.%s.rp_filter'

    check_call('sudo sysctl -w %s=0' % (rpf % 'all'), shell=True)
    check_call('sudo sysctl -w %s=0' % (rpf % interface), shell=True)


# TODO: replace the legacy code below
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
