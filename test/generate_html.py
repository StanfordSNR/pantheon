import os, sys, errno

def generate_html(size):
    file_name = '/tmp/quic-data/www.example.org/index.html'
    file_dir = os.path.dirname(file_name)

    # create file directory if it doesn't exist
    try:
        os.makedirs(file_dir)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    f = open(file_name, 'wb')
    f.write("HTTP/1.1 200 OK\n"
            "X-Original-Url: https://www.example.org/\n"
            "\n"
            "<!DOCTYPE html>\n"
            "<html>\n"
            "<body>\n"
            "<p>\n")

    i = 0
    while i < size:
        f.write('ABCDEFGHIJKLMNOPQRSTUVWXYZ\n') 
        i += 1

    f.write("</p>\n"
            "</body>\n"
            "</html>\n")

    f.close()

def main():
    size = 1000
    if len(sys.argv) == 2:
        size = int(sys.argv[1])
    generate_html(size)

if __name__ == '__main__':
    main()
