import sys, subprocess

def print_usage():
    usage = "Usage: python server.py [congestion control option] [args]\n"
    usage += "    [congestion control option]: TCP, LEDBAT, QUIC"
    example = "Example: python server.py TCP PORT"
    print usage
    print example

def main():
    if len(sys.argv) < 2:
        print_usage()
        return

    cc_option = sys.argv[1]

    if cc_option.lower() == 'tcp':
        cmd = ['./tcpserver']
        path = '../external/sourdough/examples'

    if cc_option.lower() == 'ledbat':
        cmd = ['./ucat']
        path = '../external/libutp'

    if cc_option.lower() == 'quic':
        cmd = ['./quic_server']
        path = '../external/proto-quic/src/out/Release'

    if len(sys.argv) >= 3:
        cmd += sys.argv[2:]
    subprocess.call(cmd, cwd=path)

if __name__ == '__main__':
    main()
