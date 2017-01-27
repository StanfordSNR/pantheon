#!/usr/bin/env python

from os import path
from subprocess import check_call

prefix = 'aws_brazil_to_brazil'

with open(prefix) as urls:
    for url in urls:
        url = url.strip()

        check_call(['wget', url])
        tarname = path.basename(url)
        check_call(['tar', 'xf', tarname])

        filename = tarname[:-7]
        check_call(
            'python plot_summary.py --no-plots --data-dir %s'
            ' --analyze-schemes "default_tcp vegas ledbat pcc verus scream '
            'sprout webrtc quic"' % filename,
            shell=True)

        check_call(['rm', '-rf', tarname, filename])
        break
