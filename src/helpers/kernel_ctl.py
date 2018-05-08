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


def check_qdisc(qdisc):
    curr_qdisc = check_output('sysctl net.core.default_qdisc', shell=True)
    curr_qdisc = curr_qdisc.split('=')[-1].strip()

    if qdisc != curr_qdisc:
        sys.exit('Error: current qdisc %s is not %s' % (curr_qdisc, qdisc))


def set_qdisc(qdisc):
    curr_qdisc = check_output('sysctl net.core.default_qdisc', shell=True)
    curr_qdisc = curr_qdisc.split('=')[-1].strip()

    if curr_qdisc != qdisc:
        check_call('sudo sysctl -w net.core.default_qdisc=%s' % qdisc,
                   shell=True)
        sys.stderr.write('Changed default_qdisc from %s to %s\n'
                         % (curr_qdisc, qdisc))


def enable_ip_forwarding():
    check_call('sudo sysctl -w net.ipv4.ip_forward=1', shell=True)


def disable_rp_filter(interface):
    rpf = 'net.ipv4.conf.%s.rp_filter'

    check_call('sudo sysctl -w %s=0' % (rpf % interface), shell=True)
    check_call('sudo sysctl -w %s=0' % (rpf % 'all'), shell=True)


def set_sock_recv_buf(new_default, new_max):
    buf_default = check_output('sysctl net.core.rmem_default', shell=True)
    buf_default = int(buf_default.split('=')[-1])

    buf_max = check_output('sysctl net.core.rmem_max', shell=True)
    buf_max = int(buf_max.split('=')[-1])

    if buf_default != new_default:
        check_call('sudo sysctl -w net.core.rmem_default=%s' % new_default,
                   shell=True)
        sys.stderr.write('Changed rmem_default from %s to %s\n'
                         % (buf_default, new_default))

    if buf_max != new_max:
        check_call('sudo sysctl -w net.core.rmem_max=%s' % new_max, shell=True)
        sys.stderr.write('Changed rmem_max from %s to %s\n'
                         % (buf_max, new_max))
