#!/usr/bin/env python

import os
import sys
import string
import argparse
from parse_arguments import parse_arguments
from subprocess import call, check_call, PIPE, Popen


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

    assert call(['which', 'pdflatex']) is 0, "pdflatex not installed"

    metadata = parse_metadata_file(os.path.join(test_dir, 'pantheon_metadata'))

    latex = open('/tmp/pantheon_report.tex', 'w')

    latex.write(
        '\\documentclass{article}\n'
        '\\usepackage{pdfpages, graphicx}\n'
        '\\usepackage{float}\n\n'
        '\\begin{document}\n\n'
        'Pantheon Summary\n\n'
        'Total runtime %s s; ' % metadata['runtime'])

    latex.write('%s flow' % metadata['flows'])
    if metadata['flows'] != '1':
        latex.write('s with %s s interval' % metadata['interval'])

    local_side = ''
    if 'local_info' in metadata:
        local_side += ' %s' % metadata['local_info']

    if 'local_address' in metadata:
        local_side += ' %s' % metadata['local_address']

    if 'local_interface' in metadata:
        local_side += ' on interface %s' % metadata['local_interface']

    if local_side:
        latex.write('\n\nLocal side:' + local_side)

    remote_side = ''
    if 'remote_info' in metadata:
        latex.write(' %s' % metadata['remote_info'])

    if 'remote_address' in metadata:
        latex.write(' %s' % metadata['remote_address'])

    if 'remote_interface' in metadata:
        latex.write(' on interface %s' % metadata['remote_interface'])

    if remote_side:
        latex.write('\n\nRemote side:' + remote_side)

    latex.write('\n\n\\begin{figure}[H]\n'
                '\\centering\n'
                '\\includegraphics[width=\\textwidth]'
                '{%s}\n'
                '\\end{figure}\n\n'
                '\\newpage\n\n' % pantheon_summary_png)

    for cc in args.cc_schemes:
        datalink_throughput_png = os.path.join(
            test_dir, '%s_datalink_throughput.png' % cc)
        datalink_delay_png = os.path.join(
            test_dir, '%s_datalink_delay.png' % cc)
        acklink_throughput_png = os.path.join(
            test_dir, '%s_acklink_throughput.png' % cc)
        acklink_delay_png = os.path.join(
            test_dir, '%s_acklink_delay.png' % cc)

        str_dict = {'cc_pretty_name': prettify(cc),
                    'datalink_throughput_png': datalink_throughput_png,
                    'datalink_delay_png': datalink_delay_png,
                    'acklink_throughput_png': acklink_throughput_png,
                    'acklink_delay_png': acklink_delay_png}

        latex.write(
            'Congestion Control Report of %(cc_pretty_name)s --- Data Link\n\n'
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
            'Congestion Control Report of %(cc_pretty_name)s --- ACK Link\n\n'
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

    cmd = 'pdflatex -output-directory %s /tmp/pantheon_report.tex' % test_dir
    sys.stderr.write('+ ' + cmd + '\n')
    check_call(cmd, shell=True, stdout=DEVNULL, stderr=DEVNULL)


if __name__ == '__main__':
    DEVNULL = open(os.devnull, 'w')
    main()
    DEVNULL.close()
