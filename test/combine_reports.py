#!/usr/bin/python

import os
import sys
import string
import argparse
from subprocess import check_call, PIPE, Popen


def svg2png(test_dir, cc):
    datalink_throughput_svg = os.path.join(
        test_dir, '%s_datalink_throughput.svg' % cc)
    datalink_delay_svg = os.path.join(test_dir, '%s_datalink_delay.svg' % cc)
    acklink_throughput_svg = os.path.join(
        test_dir, '%s_acklink_throughput.svg' % cc)
    acklink_delay_svg = os.path.join(test_dir, '%s_acklink_delay.svg' % cc)

    datalink_throughput_png = '/tmp/%s_datalink_throughput.png' % cc
    datalink_delay_png = '/tmp/%s_datalink_delay.png' % cc
    acklink_throughput_png = '/tmp/%s_acklink_throughput.png' % cc
    acklink_delay_png = '/tmp/%s_acklink_delay.png' % cc

    # Convert SVGs to PNGs
    sys.stderr.write('Converting SVGs to PNGs...\n')
    cvt_cmd = []
    cvt_str = 'inkscape -d 300 -z -e %s %s'
    cvt_cmd.append(cvt_str %
                   (datalink_throughput_png, datalink_throughput_svg))
    cvt_cmd.append(cvt_str % (acklink_throughput_png, acklink_throughput_svg))
    cvt_cmd.append(cvt_str % (datalink_delay_png, datalink_delay_svg))
    cvt_cmd.append(cvt_str % (acklink_delay_png, acklink_delay_svg))

    for cmd in cvt_cmd:
        sys.stderr.write('+ ' + cmd + '\n')
        proc = Popen(cmd, stdout=PIPE, stderr=DEVNULL, shell=True)
        while True:
            line = proc.stdout.readline()
            if not line:
                sys.stderr.write('Failed to convert SVG to PNG\n')
                sys.exit(1)
            if line.split(' ', 1)[0] == 'Bitmap':
                proc.terminate()
                break


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cc_schemes', metavar='congestion-control', type=str,
                        nargs='+', help='congestion control schemes')
    args = parser.parse_args()

    test_dir = os.path.abspath(os.path.dirname(__file__))
    latex = open('/tmp/pantheon-report.tex', 'w')

    latex.write('\\documentclass{article}\n'
                '\\usepackage{pdfpages, graphicx}\n'
                '\\usepackage{float}\n'
                '\\begin{document}\n')

    latex.write('\\includepdf[fitpaper]{pantheon_summary.pdf}\n')

    for cc in args.cc_schemes:
        svg2png(test_dir, cc)

        latex.write('Congestion Control Report of %s --- Data Link\n\n' %
                    string.replace(cc, '_', '\_'))

        latex.write('\\begin{figure}[H]\n\\centering\n')
        latex.write('\\includegraphics[width=\\textwidth]'
                    '{/tmp/%s_datalink_throughput.png}\n' % cc)
        latex.write('\\end{figure}\n\n')

        latex.write('\\begin{figure}[H]\n\\centering\n')
        latex.write('\\includegraphics[width=\\textwidth]'
                    '{/tmp/%s_datalink_delay.png}\n' % cc)
        latex.write('\\end{figure}\n\n')

        latex.write('\\newpage\n\n')

        latex.write('Congestion Control Report of %s --- ACK Link\n\n' %
                    string.replace(cc, '_', '\_'))

        latex.write('\\begin{figure}[H]\n\\centering\n')
        latex.write('\\includegraphics[width=\\textwidth]'
                    '{/tmp/%s_acklink_throughput.png}\n' % cc)
        latex.write('\\end{figure}\n\n')

        latex.write('\\begin{figure}[H]\n\\centering\n')
        latex.write('\\includegraphics[width=\\textwidth]'
                    '{/tmp/%s_acklink_delay.png}\n' % cc)
        latex.write('\\end{figure}\n\n')

        if cc != args.cc_schemes[-1]:
            latex.write('\\newpage\n\n')

    latex.write('\\end{document}')
    latex.close()

    cmd = 'pdflatex -output-directory %s /tmp/pantheon-report.tex' % test_dir
    sys.stderr.write('+ ' + cmd + '\n')
    check_call(cmd, shell=True, stdout=DEVNULL, stderr=DEVNULL)


if __name__ == '__main__':
    DEVNULL = open(os.devnull, 'w')
    main()
    DEVNULL.close()
