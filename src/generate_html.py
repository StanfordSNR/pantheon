import sys
import string
import random
from os import path
from helpers import make_sure_path_exists


def generate_html(output_dir, size):
    html = path.join(output_dir, 'index.html')
    make_sure_path_exists(output_dir)

    # check if index.html already exists
    if path.isfile(html) and path.getsize(html) > size:
        sys.stderr.write('index.html already exists\n')
        return

    head_text = ('HTTP/1.1 200 OK\n'
                 'X-Original-Url: https://www.example.org/\n'
                 '\n'
                 '<!DOCTYPE html>\n'
                 '<html>\n'
                 '<body>\n'
                 '<p>\n')

    foot_text = ('</p>\n'
                 '</body>\n'
                 '</html>\n')

    f = open(html, 'w')
    f.write(head_text)

    num_blocks = int(size) / 1024 + 1
    for _ in xrange(num_blocks):
        block = ''.join(random.choice(string.letters) for _ in xrange(1024))
        f.write(block + '\n')

    f.write(foot_text)
    f.close()
