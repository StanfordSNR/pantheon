#!/usr/bin/env python

import sys
import os
from os import path
import string
import random
import shutil
from subprocess import check_call
import project_root
from helpers import (
    get_open_port, print_port_for_tests, parse_arguments,
    make_sure_path_exists)


def generate_html(output_dir, size):
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

    num_blocks = int(size) / 1024 + 1
    for _ in xrange(num_blocks):
        block = ''.join(random.choice(string.letters) for _ in xrange(1024))
        html.write(block + '\n')

    html.write(foot_text)
    html.close()


def setup_quic(cc_repo, cert_dir, html_dir):
    os.environ['PATH'] += os.pathsep + path.join(cc_repo, 'depot_tools')
    cmd = ('gclient runhooks && ninja -C out/Release '
           'quic_client quic_server')
    check_call(cmd, shell=True, cwd=path.join(cc_repo, 'src'))

    # initialize an empty NSS Shared DB
    nssdb_dir = path.join(path.expanduser('~'), '.pki', 'nssdb')
    shutil.rmtree(nssdb_dir, ignore_errors=True)
    make_sure_path_exists(nssdb_dir)

    # generate certificate
    cert_pwd = path.join(cert_dir, 'cert_pwd')
    cmd = 'certutil -d %s -N -f %s' % (nssdb_dir, cert_pwd)
    check_call(cmd, shell=True)

    # trust certificate
    pem = path.join(cert_dir, '2048-sha256-root.pem')
    cmd = ('certutil -d sql:%s -A -t "C,," -n "QUIC" -i %s -f %s' %
           (nssdb_dir, pem, cert_pwd))
    check_call(cmd, shell=True)

    # generate a html of size that can be transferred longer than 60 s
    generate_html(html_dir, 5e7)


def main():
    args = parse_arguments('sender_first')

    cc_repo = path.join(project_root.DIR, 'third_party', 'proto-quic')
    send_src = path.join(cc_repo, 'src', 'out', 'Release', 'quic_server')
    recv_src = path.join(cc_repo, 'src', 'out', 'Release', 'quic_client')

    cert_dir = path.join(project_root.DIR, 'src', 'quic-certs')
    html_dir = path.join(cc_repo, 'www.example.org')
    make_sure_path_exists(html_dir)

    if args.option == 'deps':
        print 'libnss3-tools'

    if args.option == 'run_first':
        print 'sender'

    if args.option == 'setup':
        setup_quic(cc_repo, cert_dir, html_dir)

    if args.option == 'sender':
        port = get_open_port()
        print_port_for_tests(port)

        cmd = [send_src, '--port=%s' % port,
               '--quic_in_memory_cache_dir=%s' % html_dir,
               '--certificate_file=%s' % path.join(cert_dir, 'leaf_cert.pem'),
               '--key_file=%s' % path.join(cert_dir, 'leaf_cert.pkcs8')]
        check_call(cmd)

    if args.option == 'receiver':
        cmd = [recv_src, '--host=%s' % args.ip, '--port=%s' % args.port,
               'https://www.example.org/']
        # suppress stdout as it prints the huge web page received
        with open(os.devnull, 'w') as devnull:
            check_call(cmd, stdout=devnull)


if __name__ == '__main__':
    main()
