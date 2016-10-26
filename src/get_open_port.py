import socket


def get_open_port_helper(socket_type):
    s = socket.socket(socket.AF_INET, socket_type)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return str(port)


def get_open_udp_port():
    return str(10000)


def get_open_tcp_port():
    return str(10000)
