import argparse
import sys


def parse_arguments(filename):
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', action='store', dest='private_key', type=str,
                        help='identity file (private key) for ssh/scp to use')
    parser.add_argument('-r', action='store', dest='remote', type=str,
                        help='remote pantheon directory: [user@]hostname:dir')

    if filename == 'run.py' or filename == 'test.py':
        parser.add_argument('-f', action='store', dest='flows', type=int,
                            default=1, help='number of flows '
                            '(mm-tunnelclient/mm-tunnelserver pairs)')
        parser.add_argument('-t', action='store', dest='runtime', type=int,
                            default=60, help='running time of each test')

    if filename == 'test.py':
        parser.add_argument('cc', metavar='congestion-control', type=str,
                            help='name of a congestion control scheme')
    elif filename == 'setup.py':
        parser.add_argument(
            'cc', metavar='mahimahi|congestion-control', type=str,
            help='setup mahimahi before setup any congestion control')

    args = parser.parse_args()

    if hasattr(args, 'flows') and args.flows == 0 and args.remote:
        sys.stderr.write('Remote test must run at least one flow '
                         '(one pair of mm-tunnelclient/mm-tunnelserver)\n')
        sys.exit(1)

    return args
