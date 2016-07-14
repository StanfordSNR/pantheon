import sys

RECV_FIRST = 0
SEND_FIRST = 1

def print_usage(name, order):
    print "Usage:"
    print "./%s build" % name
    print "./%s setup" % name
    if order == RECV_FIRST:
        print "./%s receiver" % name
        print "./%s sender IP port" % name
    elif order == SEND_FIRST:
        print "./%s sender" % name
        print "./%s receiver IP port" % name
    sys.exit(1)

def check_args(args, name, order):
    if len(args) < 2:
        print_usage(name, order)

    option = args[1]

    if option == 'build' or option == 'setup':
        if len(args) != 2:
            print_usage(name, order)

    if option == 'receiver':
        if order == RECV_FIRST and len(args) != 2:
            print_usage(name, order)

        if order == SEND_FIRST and len(args) != 4:
            print_usage(name, order)

    if option == 'sender':
        if order == RECV_FIRST and len(args) != 4:
            print_usage(name, order)

        if order == SEND_FIRST and len(args) != 2:
            print_usage(name, order)

    if option != 'build' and option != 'setup' and \
       option != 'receiver' and option != 'sender':
        print_usage(name, order)
