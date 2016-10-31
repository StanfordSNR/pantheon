import os
import sys
import errno
import string
import random


def generate_html(output_dir, size):
    file_name = os.path.join(output_dir, 'index.html')

    # create file directory if it doesn't exist
    try:
        os.makedirs(output_dir)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    # check if index.html already exists
    if os.path.isfile(file_name) and os.path.getsize(file_name) > size:
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

    f = open(file_name, 'w')
    f.write(head_text)

    block_size = 1024
    for i in xrange(size / block_size + 1):
        block = ''.join(
            random.choice(string.letters) for _ in xrange(block_size))
        f.write(block + '\n')

    f.write(foot_text)
    f.close()
