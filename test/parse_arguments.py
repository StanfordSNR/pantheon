import argparse
import sys


def parse_arguments(filename):
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-i', metavar='IDENTITY-FILE', action='store', dest='private_key',
        help='identity file (private key) for ssh/scp to use')
    parser.add_argument(
        '-r', metavar='REMOTE:DIR', action='store', dest='remote',
        help='remote pantheon directory: [user@]hostname:dir')

    if filename == 'test.py' or filename == 'run.py':
        parser.add_argument(
            '-f', action='store', dest='flows', type=int, default=1,
            help='number of flows (mm-tunnelclient/mm-tunnelserver pairs)')
        parser.add_argument(
            '-t', action='store', dest='runtime', type=int, default=60,
            help='total runtime of test')
        parser.add_argument(
            '--interval', action='store', dest='interval', type=int,
            default=0, help='interval time between two consecutive flows')
        parser.add_argument(
            '--server-interface', action='store', dest='server_if',
            metavar='INTERFACE', help='interface to run mm-tunnelserver')
        parser.add_argument(
            '--client-interface', action='store', dest='client_if',
            metavar='INTERFACE', help='interface to run mm-tunnelclient')

    if filename == 'setup.py' or filename == 'test.py':
        parser.add_argument('cc', metavar='congestion-control',
                            help='name of a congestion control scheme')
    elif filename == 'run.py':
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '--test-only', action='store_true', dest='test_only',
            default=False, help='run test only without running setup')
        group.add_argument(
            '--setup-only', action='store_true', dest='setup_only',
            default=False, help='run setup only without running test')

    args = parser.parse_args()

    # arguments validation
    if args.remote:
        assert ':' in args.remote, '-r must be followed by [user@]hostname:dir'

    if filename == 'test.py' or filename == 'run.py':
        assert not (args.flows == 0 and args.remote), (
            'Remote test must run at least one flow (one tunnel)')
        assert args.runtime <= 60, 'Runtime cannot be greater than 60 seconds'
        assert (args.flows - 1) * args.interval < args.runtime, (
            'Interval time between flows is too long to be fit in runtime')
        if args.server_if or args.client_if:
            assert args.remote

    return args
