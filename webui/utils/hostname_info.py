import socket

def host_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def host_hostname():
    return socket.gethostname()

def host_fqdn():
    return socket.getfqdn()

def host_byaddr(addr):
    try:
        result = socket.gethostbyaddr(addr)[0]
    except:
        result = "Failed to Resolve Host."

    return result

def check_active_port(host,port):
    """ check_result = 0 means the port is open.
        Other check_result mean port is not open """

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try :
        check_result = sock.connect_ex((host,port))
        if check_result == 0:
           result = "Active"
        else:
           result = "Timeout ("+str(check_result)+")"
    except:
        result = "Attempt Failed"

    return result;
