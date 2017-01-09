#!/usr/bin/env python

import sys
import json
import uuid
import pantheon_helpers
from os import path
from time import strftime
from helpers.parse_arguments import parse_arguments
from helpers.pantheon_help import (check_call, check_output,
                                   get_friendly_names, Popen, PIPE)


class GenerateReport:
    def __init__(self, args):
        self.data_dir = path.abspath(args.data_dir)
        self.analyze_dir = path.dirname(__file__)
        self.src_dir = path.abspath(path.join(self.analyze_dir, '../src'))

        # load pantheon_metadata.json as a dictionary
        metadata_fname = path.join(args.data_dir, 'pantheon_metadata.json')
        with open(metadata_fname) as metadata_file:
            self.metadata_dict = json.load(metadata_file)

        self.run_times = self.metadata_dict['run_times']
        self.cc_schemes = self.metadata_dict['cc_schemes'].split()
        self.flows = int(self.metadata_dict['flows'])

        self.include_acklink = args.include_acklink

    def describe_metadata(self):
        metadata = self.metadata_dict

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

        git_info = None
        if 'git_information' in metadata:
            git_info = metadata['git_information']

        desc = (
            'Repeated the test of %d congestion control schemes %s.\n\n'
            'Each test lasted for %s running %s.\n\n'
            'Data path FROM %s TO %s.'
            % (len(self.cc_schemes), times, runtime, flows, send_side,
               recv_side))
        if 'ntp_addr' in metadata:
            ntp_addr = metadata['ntp_addr']
            desc += '\n\nNTP offset measured against %s.' % ntp_addr

        if git_info is not None:
            desc += (
                '\\newline\n\n'
                '\\begin{verbatim}\n'
                '%s'
                '\\end{verbatim}\n\n' % git_info)
        desc += ('\\newpage\n\n')

        return desc

    def include_summary(self):
        curr_time = strftime('%a, %d %b %Y %H:%M %z')
        raw_summary = path.join(self.data_dir, 'pantheon_summary.png')
        mean_summary = path.join(
            self.data_dir, 'pantheon_summary_mean.png')
        metadata_desc = self.describe_metadata()

        # set cwd to a directory in pantheon repository
        git_proc = Popen(['git', 'rev-parse', 'HEAD'], stdout=PIPE,
                         cwd=self.analyze_dir)
        analysis_git_head = git_proc.communicate()[0].strip()

        self.latex.write(
            '\\documentclass{article}\n'
            '\\usepackage{pdfpages, graphicx, float}\n'
            '\\usepackage{float}\n\n'
            '\\newcommand{\PantheonFig}[1]{%%\n'
            '\\begin{figure}[H]\n'
            '\\centering\n'
            '\\IfFileExists{#1}{\includegraphics[width=\\textwidth]{#1}}'
            '{Figure is missing}\n'
            '\\end{figure}}\n\n'
            '\\begin{document}\n\n'
            '\\textbf{Pantheon Summary} '
            '(Generated on %s with pantheon version %s)\n\n'
            '%s'
            '\\PantheonFig{%s}\n\n'
            '\\PantheonFig{%s}\n\n'
            '\\newpage\n\n'
            % (curr_time, analysis_git_head, metadata_desc, mean_summary,
               raw_summary))

    def include_runs(self):
        for cc in self.cc_schemes:
            cc_name = self.friendly_names[cc].strip().replace('_', '\\_')

            for run_id in xrange(1, 1 + self.run_times):
                fname = '%s_stats_run%s.log' % (cc, run_id)
                stats_log_path = path.join(self.data_dir, fname)

                if path.isfile(stats_log_path):
                    with open(stats_log_path) as stats_log:
                        stats_info = stats_log.read()
                else:
                    stats_info = '%s does not exist\n' % stats_log_path

                str_dict = {'cc_name': cc_name,
                            'run_id': run_id,
                            'stats_info': stats_info}

                link_directions = ['datalink']
                if self.include_acklink:
                    link_directions.append('acklink')

                for link_t in link_directions:
                    for metric_t in ['throughput', 'delay']:
                        graph_path = path.join(
                            self.data_dir, cc + '_%s_%s_run%s.png' %
                            (link_t, metric_t, run_id))
                        str_dict['%s_%s' % (link_t, metric_t)] = graph_path

                self.latex.write(
                    '\\begin{verbatim}\n'
                    'Run %(run_id)s: Statistics of %(cc_name)s\n\n'
                    '%(stats_info)s'
                    '\\end{verbatim}\n\n'
                    '\\newpage\n\n'
                    'Run %(run_id)s: Report of %(cc_name)s --- Data Link\n\n'
                    '\\PantheonFig{%(datalink_throughput)s}\n\n'
                    '\\PantheonFig{%(datalink_delay)s}\n\n'
                    '\\newpage\n\n' % str_dict)
                if self.include_acklink:
                    self.latex.write(
                        'Run %(run_id)s: '
                        'Report of %(cc_name)s --- ACK Link\n\n'
                        '\\PantheonFig{%(acklink_throughput)s}\n\n'
                        '\\PantheonFig{%(acklink_delay)s}\n\n' % str_dict)

                if cc != self.cc_schemes[-1] or run_id != self.run_times:
                    self.latex.write('\\newpage\n\n')

        self.latex.write('\\end{document}')

    def generate_report(self):
        self.friendly_names = get_friendly_names(self.cc_schemes)

        latex_path = '/tmp/pantheon-tmp/pantheon-report-%s.tex' % uuid.uuid4()
        self.latex = open(latex_path, 'w')
        self.include_summary()
        self.include_runs()
        self.latex.close()

        cmd = ['pdflatex', '-output-directory', self.data_dir,
               '-jobname', 'pantheon_report', latex_path]
        check_call(cmd)


def main():
    args = parse_arguments(path.basename(__file__))

    generate_report = GenerateReport(args)
    generate_report.generate_report()


if __name__ == '__main__':
    main()
