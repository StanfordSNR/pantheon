import os
import sys
import errno
import string
import random


def generate_html(size):
    file_name = '/tmp/quic-data/www.example.org/index.html'
    file_dir = os.path.dirname(file_name)

    # create file directory if it doesn't exist
    try:
        os.makedirs(file_dir)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    head_text = "HTTP/1.1 200 OK\n"\
            "X-Original-Url: https://www.example.org/\n"\
            "\n"\
            "<!DOCTYPE html>\n"\
            "<html>\n"\
            "<body>\n"\
            "<p>\n"

    foot_text = "</p>\n"\
            "</body>\n"\
            "</html>\n"

    i = len(head_text) + len(foot_text)
    # check we can actually write something
    assert (size >= i)

    f = open(file_name, 'wb')
    f.write(head_text)

    block_size = 1024
    while i < size:
        if i + block_size <= size:
            block = ''.join(
                random.choice(string.letters) for _ in range(block_size))
            f.write(block)
            i += block_size
        else:
            f.write(random.choice(string.letters))
            i += 1

    f.write(foot_text)

    f.close()
