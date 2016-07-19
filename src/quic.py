#!/usr/bin/python

import os, sys, errno
from subprocess import check_call
import usage
from generate_html import generate_html

def initialize():
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
    cmd = 'certutil -d sql:%s -A -t "C,," -n "QUIC" -i %s -f %s' \
            % (nssdb_dir, pem, cert_pwd)
    check_call(cmd, shell=True)

    # generate a html of size that can be transferred longer than 60 seconds
    generate_html(50000000)

def main():
    usage.check_args(sys.argv, os.path.basename(__file__), usage.SEND_FIRST)
    option = sys.argv[1]
    src_dir = os.path.abspath(os.path.dirname(__file__))
    submodule_dir = os.path.abspath(os.path.join(src_dir,
                                    '../third_party/proto-quic'))
    find_unused_port_file = os.path.join(src_dir, 'find_unused_port')
    quic_server = os.path.join(submodule_dir, 'src/out/Release/quic_server')
    quic_client = os.path.join(submodule_dir, 'src/out/Release/quic_client')
    DEVNULL = open(os.devnull, 'wb')

    # build dependencies
    if option == 'deps':
        dev_list='bison cdbs curl dpkg-dev elfutils devscripts fakeroot flex ' \
                 'git-core git-svn gperf libapache2-mod-php5 libasound2-dev ' \
                 'libbrlapi-dev libav-tools libbz2-dev libcairo2-dev ' \
                 'libcap-dev libcups2-dev libcurl4-gnutls-dev libdrm-dev ' \
                 'libelf-dev libffi-dev libgconf2-dev libglib2.0-dev ' \
                 'libglu1-mesa-dev libgnome-keyring-dev libgtk2.0-dev ' \
                 'libkrb5-dev libnspr4-dev libnss3-dev libpam0g-dev ' \
                 'libpci-dev libpulse-dev libsctp-dev libspeechd-dev ' \
                 'libsqlite3-dev libssl-dev libudev-dev libwww-perl ' \
                 'libxslt1-dev libxss-dev libxt-dev libxtst-dev openbox ' \
                 'patch perl php5-cgi pkg-config python-cherrypy3 ' \
                 'python-crypto python-dev python-numpy python-opencv ' \
                 'python-openssl python-psutil python-yaml rpm ruby ' \
                 'subversion wdiff zip libnss3-tools'

        lib_list = 'libatk1.0-0 libc6 libasound2 libcairo2 libcap2 libcups2 ' \
                   'libexpat1 libffi6 libfontconfig1 libfreetype6 ' \
                   'libglib2.0-0 libgnome-keyring0 libgtk2.0-0 libpam0g ' \
                   'libpango1.0-0 libpci3 libpcre3 libpixman-1-0 libpng12-0 ' \
                   'libspeechd2 libstdc++6 libsqlite3-0 libx11-6 libxau6 ' \
                   'libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxdmcp6 ' \
                   'libxext6 libxfixes3 libxi6 libxinerama1 libxrandr2 ' \
                   'libxrender1 libxtst6 zlib1g'

        sys.stderr.write(dev_list + ' ' + lib_list + '\n')

    # build
    if option == 'build':
        os.environ['PATH'] += ':%s/depot_tools' % submodule_dir
        cmd = 'cd %s/src && gclient runhooks && ninja -C out/Release ' \
              'quic_client quic_server' % submodule_dir
        check_call(cmd, shell=True)

    # commands to be run after building and before running
    if option == 'initialize':
        initialize()

    # who goes first
    if option == 'who_goes_first':
        sys.stderr.write('Sender first\n')

    # sender
    if option == 'sender':
        sys.stderr.write('Listening on port: 6121\n')
        cmd = [quic_server,
              '--quic_in_memory_cache_dir=/tmp/quic-data/www.example.org',
              '--certificate_file=%s/certs/out/leaf_cert.pem' % src_dir,
              '--key_file=%s/certs/out/leaf_cert.pkcs8' % src_dir]
        check_call(cmd, stdout=DEVNULL, stderr=DEVNULL)

    # receiver
    if option == 'receiver':
        ip = sys.argv[2]
        port = sys.argv[3]
        cmd = [quic_client, '--host=%s' % ip, '--port=%s' % port,
              'https://www.example.org/']
        check_call(cmd, stdout=DEVNULL, stderr=DEVNULL)

    DEVNULL.close()

if __name__ == '__main__':
    main()
