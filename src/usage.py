RECV_FIRST = 0
SEND_FIRST = 1

def print_usage(name, order=RECV_FIRST):
    print "Usage:" 
    print "./%s setup" % name
    if order == RECV_FIRST:
        print "./%s receiver" % name
        print "./%s sender IP port" % name
    elif order == SEND_FIRST:
        print "./%s sender" % name
        print "./%s receiver IP port" % name
