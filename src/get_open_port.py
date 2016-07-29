import socket

# adapted from http://stackoverflow.com/questions/2838244/get-open-tcp-port-in-python/2838309#2838309
def get_open_port_helper(socket_type):
    s = socket.socket(socket.AF_INET, socket_type)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind(("",0))
    port = s.getsockname()[1]
    s.close()
    return port

def get_open_udp_port():
    return get_open_port_helper(socket.SOCK_DGRAM)

def get_open_tcp_port():
    return get_open_port_helper(socket.SOCK_STREAM)
