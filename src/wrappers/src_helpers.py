import sys
import time
import signal
import argparse
import os
from os import path
from subprocess import call
import project_root
from helpers.helpers import (
    make_sure_path_exists, TMPDIR, parse_config, get_default_qdisc)


def curr_time_sec():
    return int(time.time())


def check_default_qdisc(cc):
    config = parse_config()
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


def apply_patch(patch_name, repo_dir):
    patch = path.join(project_root.DIR, 'src', 'patches', patch_name)

    if call(['git', 'apply', patch], cwd=repo_dir) != 0:
        sys.stderr.write('patch apply failed but assuming things okay '
                         '(patch applied previously?)\n')


def wait_and_kill_iperf(proc):
    def stop_signal_handler(signum, frame):
        if proc:
            os.kill(proc.pid, signal.SIGKILL)
            sys.stderr.write(
                'wait_and_kill_iperf: caught signal %s and killed iperf with '
                'pid %s\n' % (signum, proc.pid))

    signal.signal(signal.SIGINT, stop_signal_handler)
    signal.signal(signal.SIGTERM, stop_signal_handler)

    proc.wait()
