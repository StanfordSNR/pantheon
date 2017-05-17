#!/usr/bin/env python

import sys
import time
import signal
import os
from os import path
from subprocess import check_output, Popen, PIPE
import yaml


def main():
    curr_dir = path.dirname(path.abspath(__file__))
    src_dir = path.abspath(path.join(curr_dir, os.pardir))

    with open(path.join(src_dir, 'config.yml')) as config_file:
        config = yaml.load(config_file)
    schemes = config.keys()

    print 'Testing schemes...'
    for scheme in schemes:
        print '\nscheme:', scheme
        src = path.join(src_dir, scheme + '.py')

        # print dependencies
        deps = check_output([src, 'deps'])
        if deps:
            sys.stdout.write('dependencies: %s' % deps)

        run_first = check_output([src, 'run_first']).strip()
        run_second = 'receiver' if run_first == 'sender' else 'sender'

        # run first to run
        cmd = [src, run_first]
        first_proc = Popen(cmd, preexec_fn=os.setsid, stdout=PIPE)
        port = first_proc.stdout.readline().split()[-1]
        time.sleep(3)  # wait for 'run_first' to be ready

        # run second to run
        cmd = [src, run_second, '127.0.0.1', port]
        second_proc = Popen(cmd, preexec_fn=os.setsid)

        # test lasts for 3 seconds
        time.sleep(3)

        # cleanup
        os.killpg(os.getpgid(second_proc.pid), signal.SIGTERM)
        os.killpg(os.getpgid(first_proc.pid), signal.SIGTERM)


if __name__ == '__main__':
    main()
