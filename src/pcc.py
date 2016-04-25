import os, sys, subprocess
from subprocess import Popen, PIPE
from usage import general_usage

def main():
    # find paths of this script, find_unused_port and scheme source to run
    src_dir = os.path.abspath(os.path.dirname(__file__)) 
    find_unused_port_file = os.path.join(src_dir, 'find_unused_port')

    pcc_dir = os.path.abspath(os.path.join(src_dir, '../third_party/pcc'))
    recv_file = os.path.join(pcc_dir, 'receiver/app/appserver')
    send_file = os.path.join(pcc_dir, 'sender/app/appclient')

    if len(sys.argv) < 2:
        general_usage()
        return

    option = sys.argv[1]

    # setup
    if option == 'setup':
        if len(sys.argv) != 2: 
            general_usage()
            return
        sys.stderr.write("Setup done.\n")

    # receiver
    if option == 'receiver':
        if len(sys.argv) != 2: 
            general_usage()
            return

        sys.stderr.write("Listening on port: 9000\n")

        cmd = 'export LD_LIBRARY_PATH=%s && %s > /dev/null 2>&1' % \
              (os.path.join(pcc_dir, 'receiver/src'), recv_file)
        subprocess.call(cmd, shell=True)

    # sender
    if option == 'sender':
        if len(sys.argv) != 4:
            general_usage()
            return

        ip = sys.argv[2]
        port = sys.argv[3] 

        cmd = 'export LD_LIBRARY_PATH=%s && %s %s %s > /dev/null 2>&1' % \
              (os.path.join(pcc_dir, 'sender/src'), send_file, ip, port)
        subprocess.call(cmd, shell=True)
    
if __name__ == '__main__':
    main()
