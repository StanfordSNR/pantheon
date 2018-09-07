#!/usr/bin/env python

import os
from os import path
import sys
import string
import shutil
import time
from subprocess import check_call, call

import arg_parser
import context
from helpers import utils


def generate_html(output_dir, size):
    sys.stderr.write('Generating HTML to send...\n')

    html_path = path.join(output_dir, 'index.html')

    # check if index.html already exists
    if path.isfile(html_path) and path.getsize(html_path) > size:
        sys.stderr.write('index.html already exists\n')
        return

    head_text = ('HTTP/1.1 200 OK\n'
                 'X-Original-Url: https://www.example.org/\n'
                 '\n'
                 '<!DOCTYPE html>\n'
                 '<html>\n'
                 '<body>\n'
                 '<p>\n')

    foot_text = ('</p>\n'
                 '</body>\n'
                 '</html>\n')

    html = open(html_path, 'w')
    html.write(head_text)

    block_size = 100 * 1024 * 1024
    block = 'x' * block_size
    num_blocks = int(size) / block_size + 1
    for _ in xrange(num_blocks):
        html.write(block + '\n')

    html.write(foot_text)
    html.close()


def setup_quic(cc_repo, cert_dir, html_dir):
    os.environ['PROTO_QUIC_ROOT'] = path.join(cc_repo, 'src')
    os.environ['PATH'] += os.pathsep + path.join(cc_repo, 'depot_tools')

    cmd = path.join(cc_repo, 'proto_quic_tools', 'sync.sh')
    check_call(cmd, shell=True, cwd=path.join(cc_repo, 'src'))

    cmd = ('gn gen out/Default && ninja -C out/Default '
           'quic_client quic_server')
    check_call(cmd, shell=True, cwd=path.join(cc_repo, 'src'))

    # initialize an empty NSS Shared DB
    nssdb_dir = path.join(path.expanduser('~'), '.pki', 'nssdb')
    shutil.rmtree(nssdb_dir, ignore_errors=True)
    utils.make_sure_dir_exists(nssdb_dir)

    # generate certificate
    cert_pwd = path.join(cert_dir, 'cert_pwd')
    cmd = 'certutil -d %s -N -f %s' % (nssdb_dir, cert_pwd)
    check_call(cmd, shell=True)

    # trust certificate
    pem = path.join(cert_dir, '2048-sha256-root.pem')
    cmd = ('certutil -d sql:%s -A -t "C,," -n "QUIC" -i %s -f %s' %
           (nssdb_dir, pem, cert_pwd))
    check_call(cmd, shell=True)

    # generate a html of size that can be transferred longer than 30s
    generate_html(html_dir, 5 * 10**8)


def main():
    args = arg_parser.sender_first()

    cc_repo = path.join(context.third_party_dir, 'proto-quic')
    send_src = path.join(cc_repo, 'src', 'out', 'Default', 'quic_server')
    recv_src = path.join(cc_repo, 'src', 'out', 'Default', 'quic_client')

    cert_dir = path.join(context.src_dir, 'wrappers', 'quic-certs')
    html_dir = path.join(cc_repo, 'www.example.org')
    utils.make_sure_dir_exists(html_dir)

    if args.option == 'deps':
        print 'libnss3-tools libgconf-2-4'
        return

    if args.option == 'setup':
        setup_quic(cc_repo, cert_dir, html_dir)
        return

    if args.option == 'sender':
        cmd = [send_src, '--port=%s' % args.port,
               '--quic_response_cache_dir=%s' % html_dir,
               '--certificate_file=%s' % path.join(cert_dir, 'leaf_cert.pem'),
               '--key_file=%s' % path.join(cert_dir, 'leaf_cert.pkcs8')]
        check_call(cmd)
        return

    if args.option == 'receiver':
        cmd = [recv_src, '--host=%s' % args.ip, '--port=%s' % args.port,
               'https://www.example.org/']

        for _ in range(5):
            # suppress stdout as it prints the huge web page received
            with open(os.devnull, 'w') as devnull:
                if call(cmd, stdout=devnull) == 0:
                    return

            time.sleep(1)


if __name__ == '__main__':
    main()
