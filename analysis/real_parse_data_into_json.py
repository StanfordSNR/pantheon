#!/usr/bin/env python

from os import path
import sys
import json
import argparse
import multiprocessing
from multiprocessing.pool import ThreadPool
import numpy as np
from analyze_helpers import load_test_metadata, verify_schemes_with_meta
import tunnel_graph
import project_root
from helpers.helpers import parse_config, print_cmd


class Plot(object):
    def __init__(self, args):
        self.data_dir = path.abspath(args.data_dir)
        self.output_dir = args.output_dir

        metadata_path = path.join(self.data_dir, 'pantheon_metadata.json')
        meta = load_test_metadata(metadata_path)
        self.cc_schemes = verify_schemes_with_meta(args.schemes, meta)

        self.run_times = meta['run_times']
        self.flows = meta['flows']
        self.runtime = meta['runtime']

    def parse_tunnel_log(self, cc, run_id):
        log_prefix = cc
        if self.flows == 0:
            log_prefix += '_mm'

        tput = None
        delay = None
        loss = None

        error = False

        link_directions = ['datalink']

        for link_t in link_directions:
            log_name = log_prefix + '_%s_run%s.log' % (link_t, run_id)
            log_path = path.join(self.data_dir, log_name)

            if not path.isfile(log_path):
                sys.stderr.write('Warning: %s does not exist\n' % log_path)
                error = True
                continue

            print_cmd('tunnel_graph %s\n' % log_path)
            try:
                tunnel_results = tunnel_graph.TunnelGraph(
                    tunnel_log=log_path,
                    throughput_graph=None,
                    delay_graph=None).run()
            except Exception as exception:
                sys.stderr.write('Error: %s\n' % exception)
                sys.stderr.write('Warning: "tunnel_graph %s" failed but '
                                 'continued to run.\n' % log_path)
                error = True

            if error:
                continue

            if link_t == 'datalink':
                tput = tunnel_results['throughput']
                delay = tunnel_results['delay']
                loss = tunnel_results['loss']
                duration = tunnel_results['duration'] / 1000.0

                if duration < 0.8 * self.runtime:
                    sys.stderr.write(
                        'Warning: "tunnel_graph %s" had duration %.2f seconds '
                        'but should have been around %s seconds. Ignoring this'
                        ' run.\n' % (log_path, duration, self.runtime))
                    error = True

        if error:
            return None, None, None

        return tput, delay, loss

    def eval_performance(self):
        data = {}
        results = {}

        for cc in self.cc_schemes:
            data[cc] = []
            results[cc] = {}

        cc_id = 0
        run_id = 1
        pool = ThreadPool(processes=multiprocessing.cpu_count())

        while cc_id < len(self.cc_schemes):
            cc = self.cc_schemes[cc_id]
            results[cc][run_id] = pool.apply_async(
                self.parse_tunnel_log, args=(cc, run_id))

            run_id += 1
            if run_id > self.run_times:
                run_id = 1
                cc_id += 1

        for cc in self.cc_schemes:
            for run_id in xrange(1, 1 + self.run_times):
                tput, delay, loss = results[cc][run_id].get()

                if tput is None or delay is None:
                    continue

                data[cc].append((tput, delay, loss))

        return data

    def run(self):
        data = self.eval_performance()

        json_name = path.basename(self.data_dir) + '.json'
        json_path = path.join(self.output_dir, json_name)
        with open(json_path, 'w') as outfile:
            json.dump(data, outfile)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', metavar='DIR', required=True)
    parser.add_argument('--output-dir', metavar='DIR', default='.')
    parser.add_argument('--schemes', metavar='SCH1 SCH2...', required=True)
    args = parser.parse_args()

    Plot(args).run()


if __name__ == '__main__':
    main()
