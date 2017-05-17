#!/usr/bin/env python

import sys
import shutil
import os
from os import path
from subprocess import check_call
import project_root
from generate_html import generate_html
from helpers import get_open_port, parse_arguments, make_sure_path_exists


def main():
    args = parse_arguments('sender_first')

    cc_repo = path.join(project_root.DIR, 'third_party', 'proto-quic')
    send_src = path.join(cc_repo, 'src', 'out', 'Release', 'quic_server')
    recv_src = path.join(cc_repo, 'src', 'out', 'Release', 'quic_client')

    cert_dir = path.join(project_root.DIR, 'src', 'quic-certs')
    html_dir = path.join(cc_repo, 'www.example.org')

    # print build dependencies (separated by spaces)
    if args.option == 'deps':
        print 'libnss3-tools'

    # print which side runs first (sender or receiver)
    if args.option == 'run_first':
        print 'sender'

    # build the scheme
    if args.option == 'build':
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

    # initialize the scheme before running
    if args.option == 'init':
        pass

    # run sender
    if args.option == 'sender':
        port = get_open_port()
        print 'Listening on port: %s' % port
        sys.stdout.flush()

        cmd = [send_src, '--port=%s' % port,
               '--quic_in_memory_cache_dir=%s' % html_dir,
               '--certificate_file=%s' % path.join(cert_dir, 'leaf_cert.pem'),
               '--key_file=%s' % path.join(cert_dir, 'leaf_cert.pkcs8')]
        check_call(cmd)

    # run receiver
    if args.option == 'receiver':
        cmd = [recv_src, '--host=%s' % args.ip, '--port=%s' % args.port,
               'https://www.example.org/']
        # suppress stdout as it prints the huge web page received
        with open(os.devnull, 'w') as devnull:
            check_call(cmd, stdout=devnull)


if __name__ == '__main__':
    main()
