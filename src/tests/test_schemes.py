#!/usr/bin/env python

import time
import signal
import os
from os import path
from subprocess import check_output, Popen, PIPE
import project_root
from helpers.helpers import parse_config, kill_proc_group


def main():
    src_dir = path.join(project_root.DIR, 'src')

    config = parse_config()
    schemes = config.keys()

    print 'Testing schemes...'
    for scheme in schemes:
        print '\nscheme:', scheme
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
        kill_proc_group(first_proc, signal.SIGKILL)
        kill_proc_group(second_proc, signal.SIGKILL)


if __name__ == '__main__':
    main()
