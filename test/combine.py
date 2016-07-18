#!/usr/bin/python

import os, sys, string
from subprocess import check_call

def usage():
    print 'Usage:'
    print './combine.py <congestion-control-1> [<congestion-control-2> ...]'
    sys.exit(1)

def main():
    if len(sys.argv) <= 1:
        usage()

    test_dir = os.path.abspath(os.path.dirname(__file__))
    latex = '\\documentclass{article}\n' \
            '\\usepackage{graphicx}\n' \
            '\\usepackage{float}\n' \
            '\\begin{document}\n'

    for i in range(1, len(sys.argv)):
        cc = sys.argv[i]
        latex += 'Congestion Control Report of %s --- Data Link\n\n' \
                  % string.replace(cc, '_', '\_')

        latex += '\\begin{figure}[H]\n\\centering\n'
        latex += '\\includegraphics[width=\\textwidth]' \
                 '{%s_datalink_throughput.png}\n' % cc
        latex += '\\end{figure}\n\n'

        latex += '\\begin{figure}[H]\n\\centering\n'
        latex += '\\includegraphics[width=\\textwidth]' \
                 '{%s_datalink_delay.png}\n' % cc
        latex += '\\end{figure}\n\n'

        latex += '\\newpage\n\n'

        latex += 'Congestion Control Report of %s --- ACK Link\n\n' \
                  % string.replace(cc, '_', '\_')

        latex += '\\begin{figure}[H]\n\\centering\n'
        latex += '\\includegraphics[width=\\textwidth]' \
                 '{%s_acklink_throughput.png}\n' % cc
        latex += '\\end{figure}\n\n'

        latex += '\\begin{figure}[H]\n\\centering\n'
        latex += '\\includegraphics[width=\\textwidth]' \
                 '{%s_acklink_delay.png}\n' % cc
        latex += '\\end{figure}\n\n'

        if i < len(sys.argv) - 1:
            latex += '\\newpage\n\n'

    latex += '\\end{document}'

    latex_file = open('pantheon-report.tex', 'wb')
    latex_file.write(latex)
    latex_file.close()

    cmd = 'pdflatex pantheon-report.tex'
    check_call(cmd, shell=True)

if __name__ == '__main__':
    main()
