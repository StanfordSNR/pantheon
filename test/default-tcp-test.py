import sys, subprocess

def main():
    path = '../src'

    setup_cmd = 'python default-tcp.py setup'
    setup_proc = subprocess.Popen(setup_cmd, cwd = path, shell = True)
    setup_proc.communicate()

    port_proc = subprocess.Popen('./find-unused-port', cwd = path, shell = True)
    port = port_proc.communicate()[0]

    recv_cmd = 'python default-tcp.py receiver port < '
    recv_proc = subprocess.Popen(recv_cmd, cwd = path

    '''
    while True:
        output = recv_proc.stdout.readline()
        if output == '' and recv_proc.poll() is not None:
            break
        if output:
            port = output.rsplit(' ', 1)[-1]
            break
    output = recv_proc.stdout.readline()
    port = output.rsplit(' ', 1)[-1]
    print port
    '''

if __name__ == '__main__':
    main()
