import os, sys, subprocess, errno
from subprocess import Popen, PIPE
from usage import general_usage

def setup():
    # generate certificate
    certs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                'certs'))
    certs_proc = subprocess.call(['./generate-certs.sh'], cwd=certs_dir)

    # trust certificate
    pem = os.path.join(certs_dir, 'out/2048-sha256-root.pem')
    cmd = 'certutil -d sql:$HOME/.pki/nssdb -A -t "C,," -n "QUIC" -i %s' % pem
    subprocess.call(cmd, shell=True)

    # create example website served by QUIC server
    website_name = '/tmp/quic-data/www.example.org/index.html'
    website_dir = os.path.dirname(website_name)

    # create file directory if it doesn't exist
    try:
        os.makedirs(website_dir)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    f = open(website_name, 'wb')
    f.write("HTTP/1.1 200 OK\n"
            "X-Original-Url: https://www.example.org/\n"
            "\n"
            "<!DOCTYPE html>\n"
            "<html>\n"
            "<body>\n"
            "<p>\n"
            "This is an example website for QUIC.\n"
            "</p>\n"
            "</body>\n"
            "</html>\n")
    f.close()

def main():
    # find paths of this script, find_unused_port and scheme source to run
    src_dir = os.path.abspath(os.path.dirname(__file__)) 
    find_unused_port_file = os.path.join(src_dir, 'find_unused_port')
    quic_src_dir = os.path.abspath(os.path.join(src_dir,
                                    '../third_party/proto-quic/src'))
    
    quic_server = os.path.join(quic_src_dir, 'out/Release/quic_server')
    quic_client = os.path.join(quic_src_dir, 'out/Release/quic_client')

    if len(sys.argv) < 2:
        general_usage()
        return

    option = sys.argv[1]

    # setup
    if option == 'setup':
        if len(sys.argv) != 2: 
            general_usage()
            return
        setup() 
        sys.stderr.write("Setup done.\n")

    # sender
    if option == 'sender':
        if len(sys.argv) != 2: 
            general_usage()
            return

        sys.stderr.write("Listening on port: 6121\n")

        cmd = [quic_server,
              '--quic_in_memory_cache_dir=/tmp/quic-data/www.example.org',
              '--certificate_file=%s' % \
                 os.path.join(src_dir, 'certs/out/leaf_cert.pem'),
              '--key_file=%s' % \
                 os.path.join(src_dir, 'certs/out/leaf_cert.pkcs8')]
        subprocess.call(cmd)

    # receiver
    if option == 'receiver':
        if len(sys.argv) != 4:
            general_usage()
            return

        ip = sys.argv[2]
        port = sys.argv[3]
        cmd = [quic_client, '--host=%s' % ip, '--port=%s' % port,
              'https://www.example.org/']
        subprocess.call(cmd)
    
if __name__ == '__main__':
    main()
