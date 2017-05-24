#!/usr/bin/env python

import project_root
import helpers.helpers as h


def main():
    h.call(['echo', '1'])
    h.check_call('echo 2', shell=True)

    ret = h.check_output(['echo', '3']).strip()
    print ret
    assert ret == '3'

    proc = h.Popen(['echo', '4'], stdout=h.PIPE)
    ret = proc.communicate()[0].strip()
    print ret
    assert ret == '4'

    print h.get_open_port()
    h.make_sure_path_exists(h.TMPDIR)
    print h.parse_config()


if __name__ == '__main__':
    main()
