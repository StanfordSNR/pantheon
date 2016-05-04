RECV_FIRST = 0
SEND_FIRST = 1

def print_usage(option):
    print "Usage:" 
    print "./scheme.py setup"
    if option == RECV_FIRST:
        print "./scheme.py receiver"
        print "./scheme.py sender IP port"
    elif option == SEND_FIRST:
        print "./scheme.py sender"
        print "./scheme.py receiver IP port"
    else:
        print "Error in printing usage!"
