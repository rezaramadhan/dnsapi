from hostname_info import *

def hostinfo_processor(request):
    return {'host_name': host_hostname(), 'host_ip': host_ip_address()}
