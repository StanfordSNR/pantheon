#!/usr/bin/env python

import os
from os import path
import sys
import time
import signal
import argparse

import context
from helpers import utils
from helpers.subprocess_wrappers import Popen, check_output, call


def test_schemes(args):
    wrappers_dir = path.join(context.src_dir, 'wrappers')

    if args.all:
        schemes = utils.parse_config()['schemes'].keys()
    elif args.schemes is not None:
        schemes = args.schemes.split()

    for scheme in schemes:
        sys.stderr.write('Testing %s...\n' % scheme)
        src = path.join(wrappers_dir, scheme + '.py')

        run_first = check_output([src, 'run_first']).strip()
        run_second = 'receiver' if run_first == 'sender' else 'sender'

        port = utils.get_open_port()

        # run first to run
        cmd = [src, run_first, port]
        first_proc = Popen(cmd, preexec_fn=os.setsid)

        # wait for 'run_first' to be ready
        time.sleep(3)

        # run second to run
        cmd = [src, run_second, '127.0.0.1', port]
        second_proc = Popen(cmd, preexec_fn=os.setsid)

        # test lasts for 3 seconds
        signal.signal(signal.SIGALRM, utils.timeout_handler)
        signal.alarm(3)

        try:
            for proc in [first_proc, second_proc]:
                proc.wait()
                if proc.returncode != 0:
                    sys.exit('%s failed in tests' % scheme)
        except utils.TimeoutError:
            pass
        except Exception as exception:
            sys.exit('test_schemes.py: %s\n' % exception)
        else:
            signal.alarm(0)
            sys.exit('test exited before time limit')
        finally:
            # cleanup
            utils.kill_proc_group(first_proc)
            utils.kill_proc_group(second_proc)


def cleanup():
    cleanup_src = path.join(context.base_dir, 'tools', 'pkill.py')
    cmd = [cleanup_src, '--kill-dir', context.base_dir]
    call(cmd)


def main():
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all', action='store_true',
                       help='test all the schemes specified in src/config.yml')
    group.add_argument('--schemes', metavar='"SCHEME1 SCHEME2..."',
                       help='test a space-separated list of schemes')

    args = parser.parse_args()

    try:
        test_schemes(args)
    except:
        cleanup()
        raise
    else:
        sys.stderr.write('Passed all tests!\n')


if __name__ == '__main__':
    main()
