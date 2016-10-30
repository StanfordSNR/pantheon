#!/usr/bin/env python

import os
import sys
import string
import argparse
from subprocess import call, check_call, PIPE, Popen


def prettify(cc):
    pretty_name = {
        'default_tcp': 'TCP Cubic', 'vegas': 'TCP Vegas',
        'koho_cc': 'KohoCC', 'ledbat': 'LEDBAT', 'sprout': 'Sprout',
        'pcc': 'PCC', 'verus': 'Verus', 'scream': 'SCReAM',
        'webrtc': 'WebRTC media', 'quic': 'QUIC Cubic (toy)'}
    return pretty_name[cc]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cc_schemes', metavar='congestion-control',
                        nargs='+', help='congestion control schemes')
    args = parser.parse_args()

    test_dir = os.path.abspath(os.path.dirname(__file__))

    assert call(['which', 'pdflatex']) is 0, "pdflatex not installed"
    assert call(['which', 'inkscape']) is 0, "inkscape not installed"

    latex = open('/tmp/pantheon_report.tex', 'w')

    latex.write('\\documentclass{article}\n'
                '\\usepackage{pdfpages, graphicx}\n'
                '\\usepackage{float}\n\n'
                '\\begin{document}\n\n'
                'Pantheon Summary\n\n'
                '\\begin{figure}[H]\n'
                '\\centering\n'
                '\\includegraphics[width=\\textwidth]'
                '{pantheon_summary.png}\n'
                '\\end{figure}\n\n'
                '\\newpage\n\n')

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
