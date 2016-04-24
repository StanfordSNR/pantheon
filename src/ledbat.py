import os, sys, subprocess
from subprocess import Popen, PIPE
from usage import general_usage

def main():
    # find paths of this script, find_unused_port and scheme source to run
    src_dir = os.path.abspath(os.path.dirname(__file__)) 
    find_unused_port_file = os.path.join(src_dir, 'find_unused_port')
    src_file = os.path.abspath(os.path.join(src_dir,
                               '../third_party/libutp/ucat-static'))

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

        cmd = [src_file, '-l', '-p', port]
        subprocess.call(cmd)

    # sender
    if option == 'sender':
        if len(sys.argv) != 4:
            general_usage()
            return

        ip = sys.argv[2]
        port = sys.argv[3] 
        cmd = [src_file, ip, port]
        subprocess.call(cmd)
    
if __name__ == '__main__':
    main()
