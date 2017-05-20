import sys
import string
import random
from os import path


def generate_html(output_dir, size):
    html_path = path.join(output_dir, 'index.html')

    # check if index.html already exists
    if path.isfile(html_path) and path.getsize(html_path) > size:
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

    html = open(html_path, 'w')
    html.write(head_text)

    num_blocks = int(size) / 1024 + 1
    for _ in xrange(num_blocks):
        block = ''.join(random.choice(string.letters) for _ in xrange(1024))
        html.write(block + '\n')

    html.write(foot_text)
    html.close()
