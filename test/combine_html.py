#!/usr/bin/python

import glob, os

def main():
    test_dir = os.path.abspath(os.path.dirname(__file__))
    report = open('%s/integrated_report.html' % test_dir, 'wb')
    report.write(
        '<!DOCTYPE html>\n'
        '<html>\n'
        '<head>\n'
        '<title> Pantheon Report </title>\n'
        '</head>\n'
        '<body>\n'
    )

    for fname in glob.glob('%s/*.html' % test_dir):
        if fname == '%s/integrated_report.html' % test_dir:
            continue
        print fname
        f = open(fname, 'rb')
        f.readline() # <!DOCTYPE html>
        f.readline() # <html>
        f.readline() # <head>
        f.readline() # <title> ... </title>
        f.readline() # </head>
        f.readline() # <body>
        while True:
            l = f.readline()
            if l and l != '</body>\n':
                report.write(l)
            else:
                report.write('<br><br>\n')
                break
        f.close()

    report.write(
        '</body>\n'
        '</html>\n'
    )
    report.close()

if __name__ == '__main__':
    main()
