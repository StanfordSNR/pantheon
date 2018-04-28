#!/usr/bin/env python

from os import path
import project_root
import shutil
import argparse
from helpers.helpers import check_call, parse_config, make_sure_path_exists


def main():
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all', action='store_true',
                       help='test all the schemes specified in src/config.yml')
    group.add_argument('--schemes', metavar='"SCHEME1 SCHEME2..."',
                       help='test a space-separated list of schemes')

    args = parser.parse_args()

    if args.all:
        schemes = parse_config()['schemes'].keys()
    elif args.schemes is not None:
        schemes = args.schemes.split()

    curr_dir = path.abspath(path.dirname(__file__))
    data_dir = path.join(curr_dir, 'data')
    shutil.rmtree(data_dir, ignore_errors=True)
    make_sure_path_exists(data_dir)

    test_py = path.join(project_root.DIR, 'test', 'test.py')
    analyze_py = path.join(project_root.DIR, 'analysis', 'analyze.py')

    cmd = ['python', test_py, 'local', '--schemes', ' '.join(schemes),
           '-t', '10', '--data-dir', data_dir, '--pkill-cleanup',
           '--prepend-mm-cmds', 'mm-delay 20', '--extra-mm-link-args',
           '--uplink-queue=droptail --uplink-queue-args=packets=200']
    check_call(cmd)

    cmd = ['python', analyze_py, '--data-dir', data_dir]
    check_call(cmd)


if __name__ == '__main__':
    main()
