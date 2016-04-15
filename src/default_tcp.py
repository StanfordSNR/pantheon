import sys, subprocess
from usage import general_usage

def main():
    if len(sys.argv) < 2:
        general_usage()
        return

    option = sys.argv[1]

    if option == 'setup':
        sys.stderr.write("Setup done.\n")

    if option == 'receiver':
        if len(sys.argv) == 3:
            port = sys.argv[2]
        else:
            proc = subprocess.Popen(['./find_unused_port'], stdout = subprocess.PIPE)
            port = proc.communicate()[0]  
        sys.stderr.write("Listening on port: %s\n" % port)

        cmd = ['./tcpserver', port]
        path = '../external/sourdough/examples'
        subprocess.call(cmd, cwd = path)

    if option == 'sender':
        if len(sys.argv) < 4:
            general_usage()
            return
        ip = sys.argv[2]
        port = sys.argv[3] 
        cmd = ['./tcpclient', ip, port]
        path = '../external/sourdough/examples'
        subprocess.call(cmd, cwd = path)
    
if __name__ == '__main__':
    main()
