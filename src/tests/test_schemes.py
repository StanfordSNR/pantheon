#!/usr/bin/env python

import sys
import time
import os
from os import path
import project_root
from helpers.helpers import (
    check_output, call, Popen, PIPE, parse_config, kill_proc_group)


def test_schemes():
    src_dir = path.join(project_root.DIR, 'src')
    schemes = parse_config().keys()

    for scheme in schemes:
        sys.stderr.write('Testing %s...\n' % scheme)
        src = path.join(src_dir, scheme + '.py')

        run_first = check_output([src, 'run_first']).strip()
        run_second = 'receiver' if run_first == 'sender' else 'sender'

        # run first to run
        cmd = [src, run_first]
        first_proc = Popen(cmd, preexec_fn=os.setsid, stdout=PIPE)
        port = first_proc.stdout.readline().split()[-1]

        # wait for 'run_first' to be ready
        time.sleep(3)

        # run second to run
        cmd = [src, run_second, '127.0.0.1', port]
        second_proc = Popen(cmd, preexec_fn=os.setsid)

        # test lasts for 3 seconds
        time.sleep(3)

        # cleanup
        kill_proc_group(first_proc)
        kill_proc_group(second_proc)


def cleanup():
    pkill_src = path.join(project_root.DIR, 'helpers', 'pkill.py')
    cmd = ['python', pkill_src, '--kill-dir', project_root.DIR]
    call(cmd)


def main():
    try:
        test_schemes()
    except:
        cleanup()
        raise
    else:
        sys.stderr.write('Passed all tests!\n')


if __name__ == '__main__':
    main()
