import sys


def print_usage(name, order):
    print 'Usage:'
    print './%s deps' % name
    print './%s build' % name
    print './%s init' % name
    print './%s who_goes_first' % name
    print './%s friendly_name' % name
    if order == 'receiver_first':
        print './%s receiver' % name
        print './%s sender IP port' % name
    elif order == 'sender_first':
        print './%s sender' % name
        print './%s receiver IP port' % name
    sys.exit(1)


def check_args(args, name, order):
    if len(args) < 2:
        print_usage(name, order)

    option = args[1]

    if option == 'deps' or option == 'build' or option == 'init' or \
       option == 'who_goes_first' or option == 'friendly_name':
        if len(args) != 2:
            print_usage(name, order)

    elif option == 'receiver':
        if order == 'receiver_first' and len(args) != 2:
            print_usage(name, order)

        if order == 'sender_first' and len(args) != 4:
            print_usage(name, order)

    elif option == 'sender':
        if order == 'receiver_first' and len(args) != 4:
            print_usage(name, order)

        if order == 'sender_first' and len(args) != 2:
            print_usage(name, order)

    else:
        print_usage(name, order)
