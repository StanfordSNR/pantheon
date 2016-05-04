RECV_FIRST = 0
SEND_FIRST = 1

def print_usage(name, option=RECV_FIRST):
    print "Usage:" 
    print "./%s setup" % name
    if option == RECV_FIRST:
        print "./%s receiver" % name
        print "./%s sender IP port" % name
    elif option == SEND_FIRST:
        print "./%s sender" % name
        print "./%s receiver IP port" % name
