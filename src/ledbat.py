import os, sys, subprocess
from subprocess import Popen, PIPE
from usage import general_usage

def main():
    # find paths of this script, find_unused_port and scheme source to run
    script_path = os.path.dirname(__file__) 
    find_unused_port_file = os.path.join(script_path, 'find_unused_port')
    src_file = os.path.join(script_path, '../third_party/libutp/ucat-static')

    if len(sys.argv) < 2:
        general_usage()
        return

    cc_option = sys.argv[1]

    # setup
    if cc_option == 'setup':
        if len(sys.argv) != 2: 
            general_usage()
            return
        sys.stderr.write("Setup done.\n")

    # receiver
    if cc_option == 'receiver':
        if len(sys.argv) != 2: 
            general_usage()
            return

        proc = Popen([find_unused_port_file], stdout=PIPE)
        port = proc.communicate()[0]  
        sys.stderr.write("Listening on port: %s\n" % port)

        cmd = [src_file, '-l', '-p', port]
        subprocess.call(cmd)

    # sender
    if cc_option == 'sender':
        if len(sys.argv) != 4:
            general_usage()
            return

        ip = sys.argv[2]
        port = sys.argv[3] 
        cmd = [src_file, ip, port]
        subprocess.call(cmd)
    
if __name__ == '__main__':
    main()
