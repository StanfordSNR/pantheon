#!/usr/bin/env python

import sys
import uuid
import os
from os import path
from subprocess import call, check_call, check_output, Popen
import project_root
from helpers import get_open_port, parse_arguments, TMPDIR


def xvfb_in_use(display):
    cmd = 'xdpyinfo -display :%d >/dev/null 2>&1' % display
    if call(cmd, shell=True) == 0:
        return True
    return False


def main():
    args = parse_arguments('sender_first')

    cc_repo = path.join(project_root.DIR, 'third_party', 'webrtc')
    video = path.join(cc_repo, 'video.y4m')

    # print build dependencies (separated by spaces)
    if args.option == 'deps':
        deps = ('chromium-browser nodejs npm xvfb xfonts-100dpi '
                'xfonts-75dpi xfonts-cyrillic xorg dbus-x11')
        print deps

    # print which side runs first (sender or receiver)
    if args.option == 'run_first':
        print 'sender'

    # build the scheme
    if args.option == 'build':
        check_call(['npm', 'install'], cwd=cc_repo)

        # check if video already exists and if its md5 checksum is correct
        video_md5 = 'a4ef8836e546bbef4276346d0b86e81b'
        if path.isfile(video):
            md5_out = check_output(['md5sum', video]).split()[0]
        else:
            md5_out = None

        if md5_out != video_md5:
            video_url = (
                'https://media.xiph.org/video/derf/y4m/blue_sky_1080p25.y4m')
            cmd = ['wget', '-O', video, video_url]
            check_call(cmd)
        else:
            sys.stderr.write('video already exists\n')

    # initialize the scheme before running
    if args.option == 'init':
        pass

    # run sender
    if args.option == 'sender':
        if not xvfb_in_use(1):
            Popen(['Xvfb', ':1'])
        os.environ['DISPLAY'] = ':1'

        port = get_open_port()
        signaling_server_src = path.join(cc_repo, 'app.js')
        Popen(['nodejs', signaling_server_src, port])
        print 'Listening on port: %s' % port
        sys.stdout.flush()

        user_data_dir = path.join(TMPDIR, 'webrtc-%s' % uuid.uuid4())
        cmd = ['chromium-browser', '--app=http://localhost:%s/sender' % port,
               '--use-fake-ui-for-media-stream',
               '--use-fake-device-for-media-stream',
               '--use-file-for-fake-video-capture=%s' % video,
               '--user-data-dir=%s' % user_data_dir]
        check_call(cmd)

    # run receiver
    if args.option == 'receiver':
        if not xvfb_in_use(2):
            Popen(['Xvfb', ':2'])
        os.environ['DISPLAY'] = ':2'

        user_data_dir = path.join(TMPDIR, 'webrtc-%s' % uuid.uuid4())
        cmd = ['chromium-browser',
               '--app=http://%s:%s/receiver' % (args.ip, args.port),
               '--user-data-dir=%s' % user_data_dir]
        check_call(cmd)


if __name__ == '__main__':
    main()
