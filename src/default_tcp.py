import os, sys, subprocess
from subprocess import Popen, PIPE
from usage import general_usage

def main():
    src_dir = os.path.abspath(os.path.dirname(__file__))
    find_unused_port_file = os.path.join(src_dir, 'find_unused_port')
    src_file = 'iperf'

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

        proc = Popen([find_unused_port_file], stdout=PIPE)
        port = proc.communicate()[0]  
        sys.stderr.write("Listening on port: %s\n" % port)

        cmd = [src_file, '-s', '-p', port, '-t', '10']
        subprocess.call(cmd)

    # sender
    if option == 'sender':
        if len(sys.argv) != 4:
            general_usage()
            return

        ip = sys.argv[2]
        port = sys.argv[3] 
        cmd = [src_file, '-c', ip, '-p', port, '-t', '10']
        subprocess.call(cmd)

if __name__ == '__main__':
    main()
