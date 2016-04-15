import os, sys, subprocess
import time

def main():
    path = '../src'
    DEVNULL = open(os.devnull, 'wb')

    setup_cmd = 'python default_tcp.py setup'
    setup_proc = subprocess.Popen(setup_cmd, cwd = path, shell = True)
    setup_proc.communicate()

    port_proc = subprocess.Popen('./find_unused_port', cwd = path, 
                stdout = subprocess.PIPE, shell = True) 
    port = port_proc.communicate()[0]

    recv_cmd = 'python default_tcp.py receiver %s' % port
    recv_proc = subprocess.Popen(recv_cmd, cwd = path, shell = True,
                    stdout = DEVNULL, stderr = DEVNULL)

    ip = '127.0.0.1'
    send_cmd = 'python default_tcp.py sender %s %s < ../test/random_input' \
                % (ip, port)
    send_proc = subprocess.Popen(send_cmd, cwd = path, shell = True,
                    stdout = DEVNULL, stderr = DEVNULL)

    time.sleep(5)
    send_proc.terminate()
    recv_proc.terminate()

    DEVNULL.close()
    
if __name__ == '__main__':
    main()
