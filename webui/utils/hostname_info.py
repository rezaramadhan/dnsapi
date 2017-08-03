import socket

def host_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def host_hostname():
    return socket.gethostname()

def host_fqdn():
    return socket.getfqdn()
