#!/usr/bin/python

import os, sys, time, errno
from subprocess import check_output, check_call, PIPE, Popen 
import usage
from generate_html import generate_html

def print_usage():
    usage.print_usage(os.path.basename(__file__), order=usage.SEND_FIRST)
    sys.exit(1)

def setup():
    # generate a random password
    certs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'certs'))
    cert_pwd = os.path.join(certs_dir, 'cert_pwd')
    cmd = 'date +%%s | sha256sum | base64 | head -c 32 > %s' % cert_pwd 
    check_call(cmd, shell=True)

    # initialize certificate
    home_dir = os.path.abspath(os.path.expanduser('~'))
    nssdb_dir = os.path.join(home_dir, '.pki/nssdb')
    # create nssdb directory if it doesn't exist
    try:
        os.makedirs(nssdb_dir)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    cmd = 'certutil -d %s -N -f %s' % (nssdb_dir, cert_pwd)
    check_call(cmd, shell=True)

    # generate certificate
    certs_proc = check_call(['./generate-certs.sh'], cwd=certs_dir)

    # trust certificate
    pem = os.path.join(certs_dir, 'out/2048-sha256-root.pem')
    cmd = 'certutil -d sql:%s -A -t "C,," -n "QUIC" -i %s' % (nssdb_dir, pem)
    check_call(cmd, shell=True)

    # generate a html of size that can be transferred longer than 10 seconds 
    generate_html(300000)

def main():
    # find paths of this script, find_unused_port and scheme source to run
    src_dir = os.path.abspath(os.path.dirname(__file__)) 
    find_unused_port_file = os.path.join(src_dir, 'find_unused_port')
    quic_src_dir = os.path.abspath(os.path.join(src_dir,
                                    '../third_party/proto-quic/src'))
    
    quic_server = os.path.join(quic_src_dir, 'out/Release/quic_server')
    quic_client = os.path.join(quic_src_dir, 'out/Release/quic_client')

    if len(sys.argv) < 2:
        print_usage()

    option = sys.argv[1]

    # setup
    if option == 'setup':
        if len(sys.argv) != 2: 
            print_usage()

        setup() 
        sys.stderr.write("Sender first.\n")

    # sender
    if option == 'sender':
        if len(sys.argv) != 2: 
            print_usage()

        sys.stderr.write("Listening on port: 6121\n")

        cmd = [quic_server,
              '--quic_in_memory_cache_dir=/tmp/quic-data/www.example.org',
              '--certificate_file=%s' % \
                 os.path.join(src_dir, 'certs/out/leaf_cert.pem'),
              '--key_file=%s' % \
                 os.path.join(src_dir, 'certs/out/leaf_cert.pkcs8')]
        check_call(cmd)

    # receiver
    if option == 'receiver':
        if len(sys.argv) != 4:
            print_usage()

        ip = sys.argv[2]
        port = sys.argv[3]

        cmd = [quic_client, '--host=%s' % ip, '--port=%s' % port,
              'https://www.example.org/']
        check_call(cmd)
    
if __name__ == '__main__':
    main()
