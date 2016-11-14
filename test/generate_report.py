#!/usr/bin/env python

import sys
import json
import unittest
from os import path
from time import strftime
from parse_arguments import parse_arguments
from pantheon_help import check_call, check_output


class TestGenerateReport(unittest.TestCase):
    def __init__(self, test_name, args):
        super(TestGenerateReport, self).__init__(test_name)
        self.test_dir = path.abspath(path.dirname(__file__))
        self.src_dir = path.abspath(path.join(self.test_dir, '../src'))
        self.run_times = args.run_times
        self.cc_schemes = args.cc_schemes

    def get_pretty_names(self):
        self.pretty_names = {}
        for cc in self.cc_schemes:
            cc_src = path.join(self.src_dir, cc + '.py')
            cc_name = check_output(['python', cc_src, 'friendly_name']).strip()
            self.pretty_names[cc] = cc_name if cc_name else cc

    def describe_metadata(self):
        # load pantheon_metadata.json as a dictionary
        metadata_fname = path.join(self.test_dir, 'pantheon_metadata.json')
        with open(metadata_fname) as metadata_file:
            metadata = json.load(metadata_file)

        if metadata['flows'] == 1:
            flows = '1 flow'
        else:
            flows = ('%s flows with %s-second interval between two flows' %
                     (metadata['flows'], metadata['interval']))

        if metadata['runtime'] == 1:
            runtime = '1 second'
        else:
            runtime = '%s seconds' % metadata['runtime']

        run_times = metadata['run_times']
        if run_times == 1:
            times = 'once'
        elif run_times == 2:
            times = 'twice'
        else:
            times = '%s times' % run_times

        local_side = ''
        if 'local_information' in metadata:
            local_side += ' %s' % metadata['local_information']

        if 'local_address' in metadata:
            local_side += ' %s' % metadata['local_address']

        if 'local_interface' in metadata:
            local_side += ' on interface %s' % metadata['local_interface']

        if local_side:
            local_side = local_side.replace('_', '\\_')
        else:
            local_side = '\\textit{unknown}'

        remote_side = ''
        if 'remote_information' in metadata:
            remote_side += ' %s' % metadata['remote_information']

        if 'remote_address' in metadata:
            remote_side += ' %s' % metadata['remote_address']

        if 'remote_interface' in metadata:
            remote_side += ' on interface %s' % metadata['remote_interface']

        if remote_side:
            remote_side = remote_side.replace('_', '\\_')
        else:
            remote_side = '\\textit{unknown}'

        if metadata['sender_side'] == 'local':
            send_side = local_side
            recv_side = remote_side
        else:
            recv_side = local_side
            send_side = remote_side

        if 'git_information' in metadata:
            git_info = metadata['git_information']

        desc = (
            'Repeated the test of 10 congestion control schemes %s.\n\n'
            'Each test lasted for %s running %s.\n\n'
            'Data path FROM %s TO %s.\\newline\n\n'
            '\\begin{verbatim}\n'
            '%s'
            '\\end{verbatim}\n\n'
            '\\newpage\n\n'
            % (times, runtime, flows, send_side, recv_side, git_info))

        return desc

    def include_summary(self):
        curr_time = strftime('%a, %d %b %Y %H:%M:%S %z')
        raw_summary = path.join(self.test_dir, 'pantheon_summary.png')
        mean_summary = path.join(
            self.test_dir, 'pantheon_summary_mean.png')
        metadata_desc = self.describe_metadata()

        self.latex.write(
            '\\documentclass{article}\n'
            '\\usepackage{pdfpages, graphicx, float}\n'
            '\\usepackage{float}\n\n'
            '\\newcommand{\PantheonFig}[1]{%%\n'
            '\\begin{figure}[H]\n'
            '\\centering\n'
            '\\includegraphics[width=\\textwidth]{#1}\n'
            '\\end{figure}}\n\n'
            '\\begin{document}\n\n'
            '\\textbf{Pantheon Summary} (%s)\n\n'
            '%s'
            '\\PantheonFig{%s}\n\n'
            '\\PantheonFig{%s}\n\n'
            '\\newpage\n\n'
            % (curr_time, metadata_desc, mean_summary, raw_summary))

    def include_runs(self):
        for cc in self.cc_schemes:
            cc_name = self.pretty_names[cc].strip().replace('_', '\\_')

            for run_id in xrange(1, 1 + self.run_times):
                fname = '%s_stats_run%s.log' % (cc, run_id)
                stats_log_path = path.join(self.test_dir, fname)
                with open(stats_log_path) as stats_log:
                    stats_info = stats_log.read()

                fname = '%s_datalink_throughput_run%s.png' % (cc, run_id)
                datalink_throughput = path.join(self.test_dir, fname)

                fname = '%s_datalink_delay_run%s.png' % (cc, run_id)
                datalink_delay = path.join(self.test_dir, fname)

                fname = '%s_acklink_throughput_run%s.png' % (cc, run_id)
                acklink_throughput = path.join(self.test_dir, fname)

                fname = '%s_acklink_delay_run%s.png' % (cc, run_id)
                acklink_delay = path.join(self.test_dir, fname)

                str_dict = {'cc_name': cc_name,
                            'run_id': run_id,
                            'datalink_throughput': datalink_throughput,
                            'datalink_delay': datalink_delay,
                            'acklink_throughput': acklink_throughput,
                            'acklink_delay': acklink_delay,
                            'stats_info': stats_info}

                self.latex.write(
                    '\\begin{verbatim}\n'
                    'Run %(run_id)s: Statistics of %(cc_name)s\n\n'
                    '%(stats_info)s'
                    '\\end{verbatim}\n\n'
                    '\\newpage\n\n'
                    'Run %(run_id)s: Report of %(cc_name)s --- Data Link\n\n'
                    '\\PantheonFig{%(datalink_throughput)s}\n\n'
                    '\\PantheonFig{%(datalink_delay)s}\n\n'
                    '\\newpage\n\n'
                    'Run %(run_id)s: Report of %(cc_name)s --- ACK Link\n\n'
                    '\\PantheonFig{%(acklink_throughput)s}\n\n'
                    '\\PantheonFig{%(acklink_delay)s}\n\n' % str_dict)

                if cc != self.cc_schemes[-1]:
                    self.latex.write('\\newpage\n\n')

        self.latex.write('\\end{document}')

    def test_generate_report(self):
        self.get_pretty_names()

        latex_path = '/tmp/pantheon_report.tex'
        self.latex = open(latex_path, 'w')
        self.include_summary()
        self.include_runs()
        self.latex.close()

        cmd = ['pdflatex', '-output-directory', self.test_dir, latex_path]
        check_call(cmd)


def main():
    args = parse_arguments(path.basename(__file__))

    # create test suite to run
    suite = unittest.TestSuite()
    suite.addTest(TestGenerateReport('test_generate_report', args))
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)


if __name__ == '__main__':
    main()
