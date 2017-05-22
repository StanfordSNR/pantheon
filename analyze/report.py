#!/usr/bin/env python

import os
from os import path
import uuid
import project_root
from parse_arguments import parse_arguments
from helpers.helpers import (
    parse_config, check_call, check_output, TMPDIR, format_time)
from analyze_helpers import load_test_metadata, verify_schemes_with_meta


class Report(object):
    def __init__(self, args):
        self.data_dir = path.abspath(args.data_dir)
        self.include_acklink = args.include_acklink

        metadata_path = path.join(args.data_dir, 'pantheon_metadata.json')
        self.meta = load_test_metadata(metadata_path)
        self.cc_schemes = verify_schemes_with_meta(args.schemes, self.meta)

        self.run_times = self.meta['run_times']
        self.flows = self.meta['flows']

    def describe_metadata(self):
        meta = self.meta

        if meta['flows'] == 1:
            flows = '1 flow'
        else:
            flows = ('%s flows with %s-second interval between two flows' %
                     (meta['flows'], meta['interval']))

        if meta['runtime'] == 1:
            runtime = '1 second'
        else:
            runtime = '%s seconds' % meta['runtime']

        run_times = meta['run_times']
        if run_times == 1:
            times = 'once'
        elif run_times == 2:
            times = 'twice'
        else:
            times = '%s times' % run_times

        desc = (
            'Repeated the test of %d congestion control schemes %s.\n\n'
            'Each test lasted for %s running %s.\n\n'
            % (len(self.cc_schemes), times, runtime, flows))

        if meta['mode'] == 'local':
            mm_cmd = []
            if 'prepend_mm_cmds' in meta:
                mm_cmd += meta['prepend_mm_cmds']
            mm_cmd += ['mm-link', meta['uplink_trace'], meta['downlink_trace']]
            if 'extra_mm_link_args' in meta:
                mm_cmd += meta['extra_mm_link_args']
            if 'append_mm_cmds' in meta:
                mm_cmd += meta['append_mm_cmds']

            mm_cmd = ' '.join(mm_cmd).replace('_', '\\_')

            desc += 'Tested in mahimahi: \\texttt{%s}\n\n' % mm_cmd
        elif meta['mode'] == 'remote':
            txt = {}
            for side in ['local', 'remote']:
                txt[side] = [side]

                if '%s_desc' % side in meta:
                    txt[side].append(meta['%s_desc' % side])
                if '%s_addr' % side in meta:
                    txt[side].append(meta['%s_addr' % side])
                if '%s_if' % side in meta:
                    txt[side].append('on interface %s' % meta['%s_if' % side])

                txt[side] = ' '.join(txt[side]).replace('_', '\\_')

            if meta['sender_side'] == 'remote':
                sender = txt['remote']
                receiver = txt['local']
            else:
                sender = txt['local']
                receiver = txt['remote']

            desc += 'Data path FROM %s TO %s.\n\n' % (sender, receiver)

        if 'ntp_addr' in meta:
            ntp_addr = meta['ntp_addr']
            desc += '\n\nNTP offset measured against %s.' % ntp_addr

        desc += (
            '\\begin{verbatim}\n'
            '%s'
            '\\end{verbatim}\n\n' % meta['git_summary'])
        desc += '\\newpage\n\n'

        return desc

    def include_summary(self):
        raw_summary = path.join(self.data_dir, 'pantheon_summary.png')
        mean_summary = path.join(
            self.data_dir, 'pantheon_summary_mean.png')
        power_summary = path.join(
            self.data_dir, 'pantheon_summary_power.png')

        metadata_desc = self.describe_metadata()
        git_head = check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=project_root.DIR).strip()

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
            '\\PantheonFig{%s}\n\n'
            '\\newpage\n\n'
            % (format_time(), git_head, metadata_desc,
               mean_summary, raw_summary, power_summary))

    def include_runs(self):
        config = parse_config()

        cc_id = 0
        for cc in self.cc_schemes:
            cc_id += 1
            cc_name = config[cc]['friendly_name'].strip().replace('_', '\\_')

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

        self.latex.write('\\end{document}')

    def run(self):
        latex_path = path.join(TMPDIR, 'pantheon-report-%s.tex' % uuid.uuid4())
        self.latex = open(latex_path, 'w')
        self.include_summary()
        self.include_runs()
        self.latex.close()

        cmd = ['pdflatex', '-halt-on-error', '-jobname', 'pantheon_report',
               latex_path]
        check_call(cmd, cwd=TMPDIR)

        pdf_src_path = path.join(TMPDIR, 'pantheon_report.pdf')
        pdf_dst_path = path.join(self.data_dir, 'pantheon_report.pdf')
        os.rename(pdf_src_path, pdf_dst_path)


def main():
    args = parse_arguments(path.basename(__file__))
    Report(args).run()


if __name__ == '__main__':
    main()
