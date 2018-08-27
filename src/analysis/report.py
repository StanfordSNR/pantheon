#!/usr/bin/env python

import sys
import os
from os import path
import re
import uuid
import numpy as np

import arg_parser
import context
from helpers import utils
from helpers.subprocess_wrappers import check_call, check_output


class Report(object):
    def __init__(self, args):
        self.data_dir = path.abspath(args.data_dir)
        self.include_acklink = args.include_acklink

        metadata_path = path.join(args.data_dir, 'pantheon_metadata.json')
        self.meta = utils.load_test_metadata(metadata_path)
        self.cc_schemes = utils.verify_schemes_with_meta(args.schemes, self.meta)

        self.run_times = self.meta['run_times']
        self.flows = self.meta['flows']
        self.config = utils.parse_config()

    def describe_metadata(self):
        desc = '\\centerline{\\textbf{\\large{Pantheon Report}}}\n'
        desc += '\\vspace{20pt}\n\n'
        desc += 'Generated at %s (UTC).\n\n' % utils.utc_time()

        meta = self.meta

        if meta['mode'] == 'local':
            mm_cmd = []
            if 'prepend_mm_cmds' in meta:
                mm_cmd.append(meta['prepend_mm_cmds'])
            mm_cmd += ['mm-link', meta['uplink_trace'], meta['downlink_trace']]
            if 'extra_mm_link_args' in meta:
                mm_cmd.append(meta['extra_mm_link_args'])
            if 'append_mm_cmds' in meta:
                mm_cmd.append(meta['append_mm_cmds'])

            mm_cmd = ' '.join(mm_cmd).replace('_', '\\_')

            desc += 'Tested in mahimahi: \\texttt{%s}\n\n' % mm_cmd
        elif meta['mode'] == 'remote':
            txt = {}
            for side in ['local', 'remote']:
                txt[side] = []

                if '%s_desc' % side in meta:
                    txt[side].append(meta['%s_desc' % side])

                if '%s_if' % side in meta:
                    txt[side].append('on \\texttt{%s}' % meta['%s_if' % side])

                txt[side] = ' '.join(txt[side]).replace('_', '\\_')

            if meta['sender_side'] == 'remote':
                desc += ('Data path: %s (\\textit{remote}) \\textrightarrow '
                         '%s (\\textit{local}).\n\n') % (
                             txt['remote'], txt['local'])
            else:
                desc += ('Data path: %s (\\textit{local}) \\textrightarrow '
                         '%s (\\textit{remote}).\n\n') % (
                             txt['local'], txt['remote'])

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

        desc += (
            'Repeated the test of %d congestion control schemes %s.\n\n'
            'Each test lasted for %s running %s.\n\n'
            % (len(self.cc_schemes), times, runtime, flows))

        if 'ntp_addr' in meta:
            desc += ('NTP offsets were measured against \\texttt{%s} and have '
                     'been applied to correct the timestamps in logs.\n\n'
                     % meta['ntp_addr'])

        desc += (
            '\\begin{verbatim}\n'
            'System info:\n'
            '%s'
            '\\end{verbatim}\n\n' % utils.get_sys_info())

        desc += (
            '\\begin{verbatim}\n'
            'Git summary:\n'
            '%s'
            '\\end{verbatim}\n\n' % meta['git_summary'])
        desc += '\\newpage\n\n'

        return desc

    def create_table(self, data):
        align = ' c | c'
        for data_t in ['tput', 'delay', 'loss']:
            align += ' | ' + ' '.join(['Y' for _ in xrange(self.flows)])
        align += ' '

        flow_cols = ' & '.join(
            ['flow %d' % flow_id for flow_id in xrange(1, 1 + self.flows)])

        table_width = 0.9 if self.flows == 1 else ''
        table = (
            '\\begin{landscape}\n'
            '\\centering\n'
            '\\begin{tabularx}{%(width)s\linewidth}{%(align)s}\n'
            '& & \\multicolumn{%(flows)d}{c|}{mean avg tput (Mbit/s)}'
            ' & \\multicolumn{%(flows)d}{c|}{mean 95th-\\%%ile delay (ms)}'
            ' & \\multicolumn{%(flows)d}{c}{mean loss rate (\\%%)} \\\\\n'
            'scheme & \\# runs & %(flow_cols)s & %(flow_cols)s & %(flow_cols)s'
            ' \\\\\n'
            '\\hline\n'
        ) % {'width': table_width,
             'align': align,
             'flows': self.flows,
             'flow_cols': flow_cols}

        for cc in self.cc_schemes:
            flow_data = {}
            for data_t in ['tput', 'delay', 'loss']:
                flow_data[data_t] = []
                for flow_id in xrange(1, self.flows + 1):
                    if data[cc][flow_id][data_t]:
                        mean_value = np.mean(data[cc][flow_id][data_t])
                        flow_data[data_t].append('%.2f' % mean_value)
                    else:
                        flow_data[data_t].append('N/A')

            table += (
                '%(name)s & %(valid_runs)s & %(flow_tputs)s & '
                '%(flow_delays)s & %(flow_losses)s \\\\\n'
            ) % {'name': data[cc]['name'],
                 'valid_runs': data[cc]['valid_runs'],
                 'flow_tputs': ' & '.join(flow_data['tput']),
                 'flow_delays': ' & '.join(flow_data['delay']),
                 'flow_losses': ' & '.join(flow_data['loss'])}

        table += (
            '\\end{tabularx}\n'
            '\\end{landscape}\n\n'
        )

        return table

    def summary_table(self):
        data = {}

        re_tput = lambda x: re.match(r'Average throughput: (.*?) Mbit/s', x)
        re_delay = lambda x: re.match(
            r'95th percentile per-packet one-way delay: (.*?) ms', x)
        re_loss = lambda x: re.match(r'Loss rate: (.*?)%', x)

        for cc in self.cc_schemes:
            data[cc] = {}
            data[cc]['valid_runs'] = 0

            cc_name = self.config['schemes'][cc]['name']
            cc_name = cc_name.strip().replace('_', '\\_')
            data[cc]['name'] = cc_name

            for flow_id in xrange(1, self.flows + 1):
                data[cc][flow_id] = {}

                data[cc][flow_id]['tput'] = []
                data[cc][flow_id]['delay'] = []
                data[cc][flow_id]['loss'] = []

            for run_id in xrange(1, 1 + self.run_times):
                fname = '%s_stats_run%s.log' % (cc, run_id)
                stats_log_path = path.join(self.data_dir, fname)

                if not path.isfile(stats_log_path):
                    continue

                stats_log = open(stats_log_path)

                valid_run = False
                flow_id = 1

                while True:
                    line = stats_log.readline()
                    if not line:
                        break

                    if 'Datalink statistics' in line:
                        valid_run = True
                        continue

                    if 'Flow %d' % flow_id in line:
                        ret = re_tput(stats_log.readline())
                        if ret:
                            ret = float(ret.group(1))
                            data[cc][flow_id]['tput'].append(ret)

                        ret = re_delay(stats_log.readline())
                        if ret:
                            ret = float(ret.group(1))
                            data[cc][flow_id]['delay'].append(ret)

                        ret = re_loss(stats_log.readline())
                        if ret:
                            ret = float(ret.group(1))
                            data[cc][flow_id]['loss'].append(ret)

                        if flow_id < self.flows:
                            flow_id += 1

                stats_log.close()

                if valid_run:
                    data[cc]['valid_runs'] += 1

        return self.create_table(data)

    def include_summary(self):
        raw_summary = path.join(self.data_dir, 'pantheon_summary.pdf')
        mean_summary = path.join(
            self.data_dir, 'pantheon_summary_mean.pdf')

        metadata_desc = self.describe_metadata()

        self.latex.write(
            '\\documentclass{article}\n'
            '\\usepackage{pdfpages, graphicx, float}\n'
            '\\usepackage{tabularx, pdflscape}\n'
            '\\usepackage{textcomp}\n\n'
            '\\newcolumntype{Y}{>{\\centering\\arraybackslash}X}\n'
            '\\newcommand{\PantheonFig}[1]{%%\n'
            '\\begin{figure}[H]\n'
            '\\centering\n'
            '\\IfFileExists{#1}{\includegraphics[width=\\textwidth]{#1}}'
            '{Figure is missing}\n'
            '\\end{figure}}\n\n'
            '\\begin{document}\n'
            '%s'
            '\\PantheonFig{%s}\n\n'
            '\\PantheonFig{%s}\n\n'
            '\\newpage\n\n'
            % (metadata_desc, mean_summary, raw_summary))

        self.latex.write('%s\\newpage\n\n' % self.summary_table())

    def include_runs(self):
        cc_id = 0
        for cc in self.cc_schemes:
            cc_id += 1
            cc_name = self.config['schemes'][cc]['name']
            cc_name = cc_name.strip().replace('_', '\\_')

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
                        '\\PantheonFig{%(acklink_delay)s}\n\n'
                        '\\newpage\n\n' % str_dict)

        self.latex.write('\\end{document}')

    def run(self):
        report_uid = uuid.uuid4()
        latex_path = path.join(utils.tmp_dir, 'pantheon_report_%s.tex' % report_uid)
        self.latex = open(latex_path, 'w')
        self.include_summary()
        self.include_runs()
        self.latex.close()

        cmd = ['pdflatex', '-halt-on-error', '-jobname',
               'pantheon_report_%s' % report_uid, latex_path]
        check_call(cmd, cwd=utils.tmp_dir)

        pdf_src_path = path.join(utils.tmp_dir, 'pantheon_report_%s.pdf' % report_uid)
        pdf_dst_path = path.join(self.data_dir, 'pantheon_report.pdf')
        os.rename(pdf_src_path, pdf_dst_path)

        sys.stderr.write(
            'Saved pantheon_report.pdf in %s\n' % self.data_dir)


def main():
    args = arg_parser.parse_report()
    Report(args).run()


if __name__ == '__main__':
    main()
