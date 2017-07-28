import socket;

def check_active_port(host,port):
    check_result = -1

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try :
        check_result = sock.connect_ex((host,port))

        print check_result
        if check_result == 0:
           result = "Active"
        else:
           result = "Timeout ("+str(check_result)+")"
    except:
        result = 'Attempt Failed'

    # check_result = 0 means the port is open.
    # check_result = -1 defined that socket connection attempt is failed
    # Other check_result mean port is not open

    return result;