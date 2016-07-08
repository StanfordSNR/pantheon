#!/usr/bin/python

import os, sys, time
from subprocess import check_call
import usage

def print_usage():
    usage.print_usage(os.path.basename(__file__), order=usage.SEND_FIRST)
    sys.exit(1)

def main():
    # find paths of this script, find_unused_port and scheme source to run
    src_dir = os.path.abspath(os.path.dirname(__file__))
    src_file = os.path.abspath(os.path.join(src_dir,
                               '../third_party/webrtc/app.js'))
    video_file = os.path.abspath('/tmp/video.y4m')
    DEVNULL = open(os.devnull, 'wb')

    if len(sys.argv) < 2:
        print_usage()

    option = sys.argv[1]

    # setup
    if option == 'setup':
        if len(sys.argv) != 2:
            print_usage()

        sys.stderr.write("Sender first\n")

    # sender
    if option == 'sender':
        if len(sys.argv) != 2:
            print_usage()

        sys.stderr.write("Listening on port: %s\n" % 3000)

        cmd = 'chromium-browser --app=http://localhost:3000/sender ' \
              '--use-fake-ui-for-media-stream ' \
              '--use-fake-device-for-media-stream ' \
              '--use-file-for-fake-video-capture=%s ' \
              '--user-data-dir=/tmp/nonexistent$(date +%%s%%N)' % video_file
        check_call(cmd, stdout=DEVNULL, stderr=DEVNULL, shell=True)

    # receiver
    if option == 'receiver':
        if len(sys.argv) != 4:
            print_usage()

        ip = sys.argv[2]
        port = sys.argv[3]

        time.sleep(3) # at least wait until the sender is ready
        cmd = 'chromium-browser --app=http://%s:%s/receiver ' \
              '--user-data-dir=/tmp/nonexistent$(date +%%s%%N)' % (ip, port)
        check_call(cmd, stdout=DEVNULL, stderr=DEVNULL, shell=True)

    DEVNULL.close()

if __name__ == '__main__':
    main()
