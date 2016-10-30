#!/usr/bin/env python

import os
import sys
import time
import usage
import subprocess
from subprocess import check_call, check_output, PIPE, Popen
from get_open_port import get_open_udp_port


def xvfb_in_use(display):
    try:
        cmd = 'xdpyinfo -display :%d >/dev/null 2>&1' % display
        check_call(cmd, shell=True)
    except subprocess.CalledProcessError:
        return 0
    else:
        return 1


def main():
    usage.check_args(sys.argv, os.path.basename(__file__), usage.SEND_FIRST)
    option = sys.argv[1]
    src_dir = os.path.abspath(os.path.dirname(__file__))
    submodule_dir = os.path.abspath(
        os.path.join(src_dir, '../third_party/webrtc'))
    src_file = os.path.join(submodule_dir, 'app.js')
    video_file = os.path.abspath('/tmp/video.y4m')
    video_md5 = 'a4ef8836e546bbef4276346d0b86e81b'

    # build dependencies
    if option == 'deps':
        deps_list = ('chromium-browser nodejs npm xvfb xfonts-100dpi '
                     'xfonts-75dpi xfonts-cyrillic xorg dbus-x11')
        print deps_list

    # build
    if option == 'build':
        cmd = 'cd %s && npm install' % submodule_dir
        check_call(cmd, shell=True)

    # commands to be run after building and before running
    if option == 'init':
        # check if video already exists and if its md5 checksum is correct
        cmd = ['md5sum', video_file]
        md5_proc = Popen(cmd, stdout=PIPE)
        md5_out = md5_proc.communicate()[0]

        if md5_proc.returncode != 0 or md5_out.split()[0] != video_md5:
            video_url = (
                'https://media.xiph.org/video/derf/y4m/blue_sky_1080p25.y4m')
            cmd = ['wget', '-O', video_file, video_url]
            check_call(cmd)

            cmd = ['md5sum', video_file]
            assert(check_output(cmd).split()[0] == video_md5)

    # who goes first
    if option == 'who_goes_first':
        print 'Sender first'

    # sender
    if option == 'sender':
        if not xvfb_in_use(1):
            cmd = ['Xvfb', ':1']
            xvfb = Popen(cmd)
        os.environ['DISPLAY'] = ':1'

        port = get_open_udp_port()
        cmd = ['nodejs', src_file, port]
        signaling_server = Popen(cmd)
        print 'Listening on port: %s' % port
        sys.stdout.flush()

        cmd = ('chromium-browser --app=http://localhost:%s/sender '
               '--use-fake-ui-for-media-stream '
               '--use-fake-device-for-media-stream '
               '--use-file-for-fake-video-capture=%s '
               '--user-data-dir=/tmp/nonexistent$(date +%%s%%N)'
               % (port, video_file))
        check_call(cmd, shell=True)

    # receiver
    if option == 'receiver':
        if not xvfb_in_use(2):
            cmd = ['Xvfb', ':2']
            xvfb = Popen(cmd)
        os.environ['DISPLAY'] = ':2'

        ip = sys.argv[2]
        port = sys.argv[3]
        cmd = ('chromium-browser --app=http://%s:%s/receiver '
               '--user-data-dir=/tmp/nonexistent$(date +%%s%%N)' % (ip, port))

        check_call(cmd, shell=True)


if __name__ == '__main__':
    main()
