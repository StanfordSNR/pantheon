#!/usr/bin/env python

import os
import sys
import string
import argparse
from parse_arguments import parse_arguments
from subprocess import call, check_call, PIPE, Popen
from time import gmtime, strftime


def prettify(cc):
    pretty_name = {
        'default_tcp': 'TCP Cubic', 'vegas': 'TCP Vegas',
        'koho_cc': 'KohoCC', 'ledbat': 'LEDBAT', 'sprout': 'Sprout',
        'pcc': 'PCC', 'verus': 'Verus', 'scream': 'SCReAM',
        'webrtc': 'WebRTC media', 'quic': 'QUIC Cubic (toy)'}
    return pretty_name[cc]


def parse_metadata_file(metadata_fname):
    metadata_file = open(metadata_fname)

    metadata = {}
    for line in metadata_file:
        (meta_key, meta_value) = line.split('=')
        metadata[meta_key] = meta_value.strip()

    metadata_file.close()
    return metadata


def main():
    args = parse_arguments(os.path.basename(__file__))

    test_dir = os.path.abspath(os.path.dirname(__file__))
    pantheon_summary_png = os.path.join(test_dir, 'pantheon_summary.png')
    metadata = parse_metadata_file(os.path.join(test_dir, 'pantheon_metadata'))

    latex = open('/tmp/pantheon_report.tex', 'w')

    curr_time = strftime("%a, %d %b %Y %H:%M:%S %z")
    latex.write(
        '\\documentclass{article}\n'
        '\\usepackage{pdfpages, graphicx}\n'
        '\\usepackage{float}\n\n'
        '\\begin{document}\n\n'
        '\\textbf{Pantheon Summary} (%s)\n\n' % curr_time)

    if metadata['flows'] == '1':
        flows_str = '1 flow'
    else:
        flows_str = ('%s flows with %s-second interval between two flows' %
                     (metadata['flows'], metadata['interval']))

    if metadata['runtime'] == '1':
        seconds_str = '1 second'
    else:
        seconds_str = '%s seconds' % metadata['runtime']

    run_times = int(metadata['run_times'])
    if run_times == 1:
        times_str = 'once'
    elif run_times == 2:
        times_str = 'twice'
    else:
        times_str = '%s times' % run_times

    latex.write('Repeated the test of 10 congestion control schemes %s. '
                'Each test lasted for %s running %s.' %
                (times_str, seconds_str, flows_str))

    local_side = ''
    if 'local_information' in metadata:
        local_side += ' %s' % metadata['local_information']

    if 'local_address' in metadata:
        local_side += ' %s' % metadata['local_address']

    if 'local_interface' in metadata:
        local_side += ' on interface %s' % metadata['local_interface']

    if local_side:
        latex.write('\n\nLocal side:' + local_side.replace('_', '\\_'))

    remote_side = ''
    if 'remote_information' in metadata:
        remote_side += ' %s' % metadata['remote_information']

    if 'remote_address' in metadata:
        remote_side += ' %s' % metadata['remote_address']

    if 'remote_interface' in metadata:
        remote_side += ' on interface %s' % metadata['remote_interface']

    if remote_side:
        latex.write('\n\nRemote side:' + remote_side.replace('_', '\\_'))

    latex.write('\n\n\\begin{figure}[H]\n'
                '\\centering\n'
                '\\includegraphics[width=\\textwidth]'
                '{%s}\n'
                '\\end{figure}\n\n'
                '\\newpage\n\n' % pantheon_summary_png)

    for cc in args.cc_schemes:
        for run_id in xrange(1, 1 + run_times):
            datalink_throughput_png = os.path.join(
                test_dir, '%s_datalink_throughput_run%s.png' % (cc, run_id))
            datalink_delay_png = os.path.join(
                test_dir, '%s_datalink_delay_run%s.png' % (cc, run_id))
            acklink_throughput_png = os.path.join(
                test_dir, '%s_acklink_throughput_run%s.png' % (cc, run_id))
            acklink_delay_png = os.path.join(
                test_dir, '%s_acklink_delay_run%s.png' % (cc, run_id))

            str_dict = {'cc_name': prettify(cc),
                        'run_id': run_id,
                        'datalink_throughput_png': datalink_throughput_png,
                        'datalink_delay_png': datalink_delay_png,
                        'acklink_throughput_png': acklink_throughput_png,
                        'acklink_delay_png': acklink_delay_png}

            latex.write(
                'Run %(run_id)s: Report of %(cc_name)s --- Data Link\n\n'
                '\\begin{figure}[H]\n'
                '\\centering\n'
                '\\includegraphics[width=\\textwidth]'
                '{%(datalink_throughput_png)s}\n'
                '\\end{figure}\n\n'
                '\\begin{figure}[H]\n'
                '\\centering\n'
                '\\includegraphics[width=\\textwidth]'
                '{%(datalink_delay_png)s}\n'
                '\\end{figure}\n\n'
                '\\newpage\n\n'
                'Run %(run_id)s: Report of %(cc_name)s --- ACK Link\n\n'
                '\\begin{figure}[H]\n'
                '\\centering\n'
                '\\includegraphics[width=\\textwidth]'
                '{%(acklink_throughput_png)s}\n'
                '\\end{figure}\n\n'
                '\\begin{figure}[H]\n'
                '\\centering\n'
                '\\includegraphics[width=\\textwidth]'
                '{%(acklink_delay_png)s}\n'
                '\\end{figure}\n\n' % str_dict)

            if cc != args.cc_schemes[-1]:
                latex.write('\\newpage\n\n')

    latex.write('\\end{document}')
    latex.close()

    assert call(['which', 'pdflatex'], stdout=DEVNULL) is 0, (
        'pdflatex not installed')
    cmd = 'pdflatex -output-directory %s /tmp/pantheon_report.tex' % test_dir
    sys.stderr.write('+ ' + cmd + '\n')
    check_call(cmd, shell=True)


if __name__ == '__main__':
    DEVNULL = open(os.devnull, 'w')
    main()
    DEVNULL.close()
