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


def set_default_qdisc(qdisc):
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
