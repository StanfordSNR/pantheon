#!/usr/bin/env python

import os
from os import path
import sys
import uuid
from subprocess import call, check_call, check_output, Popen

import arg_parser
import context
from helpers import utils


def xvfb_in_use(display):
    cmd = 'xdpyinfo -display :%d >/dev/null 2>&1' % display
    return call(cmd, shell=True) == 0


def setup_webrtc(cc_repo, video):
    check_call(['npm', 'install'], cwd=cc_repo)

    # check if video already exists and if its md5 checksum is correct
    video_md5 = 'cd1cc8b69951796b72419413faed493b'
    if path.isfile(video):
        md5_out = check_output(['md5sum', video]).split()[0]
    else:
        md5_out = None

    if md5_out != video_md5:
        cmd = ['wget', '-O', video,
               'https://s3.amazonaws.com/stanford-pantheon/files/bluesky_1080p60.y4m']
        check_call(cmd)
    else:
        sys.stderr.write('video already exists\n')


def main():
    args = arg_parser.sender_first()

    cc_repo = path.join(context.third_party_dir, 'webrtc')
    video = path.join(cc_repo, 'video.y4m')

    if args.option == 'deps':
        print ('chromium-browser xvfb xfonts-100dpi xfonts-75dpi '
               'xfonts-cyrillic xorg dbus-x11 npm nodejs')
        return

    if args.option == 'setup':
        setup_webrtc(cc_repo, video)
        return

    if args.option == 'sender':
        if not xvfb_in_use(1):
            xvfb_proc = Popen(['Xvfb', ':1'])
        else:
            xvfb_proc = None
        os.environ['DISPLAY'] = ':1'

        # run signaling server on the sender side
        signaling_server_src = path.join(cc_repo, 'app.js')
        Popen(['node', signaling_server_src, args.port])

        user_data_dir = path.join(utils.tmp_dir, 'webrtc-%s' % uuid.uuid4())
        cmd = ['chromium-browser',
               '--app=http://localhost:%s/sender' % args.port,
               '--use-fake-ui-for-media-stream',
               '--use-fake-device-for-media-stream',
               '--use-file-for-fake-video-capture=%s' % video,
               '--user-data-dir=%s' % user_data_dir]
        check_call(cmd)
        if xvfb_proc:
            xvfb_proc.kill()
        return

    if args.option == 'receiver':
        if not xvfb_in_use(2):
            xvfb_proc = Popen(['Xvfb', ':2'])
        else:
            xvfb_proc = None
        os.environ['DISPLAY'] = ':2'

        user_data_dir = path.join(utils.tmp_dir, 'webrtc-%s' % uuid.uuid4())
        cmd = ['chromium-browser',
               '--app=http://%s:%s/receiver' % (args.ip, args.port),
               '--user-data-dir=%s' % user_data_dir]
        check_call(cmd)
        if xvfb_proc:
            xvfb_proc.kill()
        return


if __name__ == '__main__':
    main()
