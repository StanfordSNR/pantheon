#!/usr/bin/env python

from os import path
import shutil
import argparse

import context
from helpers import utils
from helpers.subprocess_wrappers import check_call


def main():
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all', action='store_true',
                       help='test all the schemes specified in src/config.yml')
    group.add_argument('--schemes', metavar='"SCHEME1 SCHEME2..."',
                       help='test a space-separated list of schemes')

    args = parser.parse_args()

    if args.all:
        schemes = utils.parse_config()['schemes'].keys()
    elif args.schemes is not None:
        schemes = args.schemes.split()

    data_dir = path.join(utils.tmp_dir, 'test_analyze_output')
    shutil.rmtree(data_dir, ignore_errors=True)
    utils.make_sure_dir_exists(data_dir)

    test_py = path.join(context.src_dir, 'experiments', 'test.py')
    analyze_py = path.join(context.src_dir, 'analysis', 'analyze.py')

    cmd = ['python', test_py, 'local', '--schemes', ' '.join(schemes),
           '-t', '10', '--data-dir', data_dir, '--pkill-cleanup',
           '--prepend-mm-cmds', 'mm-delay 20', '--extra-mm-link-args',
           '--uplink-queue=droptail --uplink-queue-args=packets=200']
    check_call(cmd)

    cmd = ['python', analyze_py, '--data-dir', data_dir]
    check_call(cmd)


if __name__ == '__main__':
    main()
