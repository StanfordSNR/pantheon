import sys, subprocess
from usage import general_usage

def main():
    if len(sys.argv) < 2:
        general_usage()
        return

    option = sys.argv[1]

    if option == 'setup':
        print "Done."

    if option == 'receiver':
        proc = subprocess.Popen(['./find-unused-port'], stdout = subprocess.PIPE)
        port = proc.communicate()[0]  
        print "Listening on port:", port
        cmd = ['./tcpserver', port]
        path = '../external/sourdough/examples'
        subprocess.call(cmd, cwd = path)

    if option == 'sender':
        ip = sys.argv[2]
        port = sys.argv[3] 
        cmd = ['./tcpclient', ip, port]
        path = '../external/sourdough/examples'
        subprocess.call(cmd, cwd = path)
    
if __name__ == '__main__':
    main()
