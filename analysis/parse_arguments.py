import sys
import argparse
from os import path
import project_root
from helpers.helpers import parse_config


def verify_schemes(schemes):
    schemes = schemes.split()
    all_schemes = parse_config().keys()

    for cc in schemes:
        if cc not in all_schemes:
            sys.exit('%s is not a scheme included in src/config.yml' % cc)


def parse_tunnel_graph():
    parser = argparse.ArgumentParser(
        description='evaluate throughput and delay of a tunnel log and '
        'generate graphs')

    parser.add_argument('tunnel_log', metavar='tunnel-log',
                        help='tunnel log file')
    parser.add_argument(
        '--throughput', metavar='OUTPUT-GRAPH',
        action='store', dest='throughput_graph',
        help='throughput graph to save as (default None)')
    parser.add_argument(
        '--delay', metavar='OUTPUT-GRAPH',
        action='store', dest='delay_graph',
        help='delay graph to save as (default None)')
    parser.add_argument(
        '--ms-per-bin', metavar='MS-PER-BIN', type=int, default=500,
        help='bin size in ms (default 500)')

    args = parser.parse_args()
    return args


def parse_analyze_shared(parser):
    parser.add_argument(
        '--schemes', metavar='"SCHEME1 SCHEME2..."',
        help='analyze a space-separated list of schemes '
        '(default: "cc_schemes" in pantheon_metadata.json)')
    parser.add_argument(
        '--data-dir', metavar='DIR',
        default=path.join(project_root.DIR, 'test', 'data'),
        help='directory that contains logs and metadata '
        'of pantheon tests (default pantheon/test/data)')


def parse_plot():
    parser = argparse.ArgumentParser(
        description='plot throughput and delay graphs for schemes in tests')

    parse_analyze_shared(parser)
    parser.add_argument('--include-acklink', action='store_true',
                        help='include acklink analysis')
    parser.add_argument(
        '--no-graphs', action='store_true', help='only append datalink '
        'statistics to stats files with no graphs generated')

    args = parser.parse_args()
    if args.schemes is not None:
        verify_schemes(args.schemes)

    return args


def parse_report():
    parser = argparse.ArgumentParser(
        description='generate a PDF report that summarizes test results')

    parse_analyze_shared(parser)
    parser.add_argument('--include-acklink', action='store_true',
                        help='include acklink analysis')

    args = parser.parse_args()
    if args.schemes is not None:
        verify_schemes(args.schemes)

    return args


def parse_analyze():
    parser = argparse.ArgumentParser(
        description='call plot.py and report.py')

    parse_analyze_shared(parser)
    parser.add_argument('--include-acklink', action='store_true',
                        help='include acklink analysis')

    args = parser.parse_args()
    if args.schemes is not None:
        verify_schemes(args.schemes)

    return args


def parse_over_time():
    parser = argparse.ArgumentParser(
        description='plot a throughput-time graph for schemes in tests')

    parse_analyze_shared(parser)
    parser.add_argument(
        '--ms-per-bin', metavar='MS-PER-BIN', type=int, default=500,
        help='bin size in ms (default 500)')
    parser.add_argument(
        '--amplify', metavar='FACTOR', type=float, default=1.0,
        help='amplication factor of output graph\'s x-axis scale ')

    args = parser.parse_args()
    if args.schemes is not None:
        verify_schemes(args.schemes)

    return args


def parse_arguments(filename):
    if filename == 'tunnel_graph.py':
        return parse_tunnel_graph()
    elif filename == 'plot.py':
        return parse_plot()
    elif filename == 'report.py':
        return parse_report()
    elif filename == 'analyze.py':
        return parse_analyze()
    elif filename == 'plot_over_time.py':
        return parse_over_time()
