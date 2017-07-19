"""Setting for file and server locations."""
# server DICT, tuple hostname, username, sama nama zone.
# login ssh via public keys
import iscpy
import json
import re
import subprocess

DEFAULT_CONF_FILENAME = "named.conf.local"
REMOTE_CONF_DIR = "/etc/named/"
USER_DICT = {"10.0.2.11": "root", "10.0.2.6": "root"}
LOCAL_DIR_DICT = {"10.0.2.11": "/mnt/nfs-dns-coba1/",
                  "10.0.2.6": "/mnt/nfs-dns-coba2/"}
ZONE_DICT = {"10.0.2.11": [], "10.0.2.6": []}

# di-populate sama script nanti dibawah
FILE_LOCATION = {}


# jangan lupa mount dulu, either pake nfs atau pake sshfs
# ngisi file_location, traversal di directory /mnt/nfs-dns-*, cari file
def get_all_zone():
    for server in LOCAL_DIR_DICT:
        with open(LOCAL_DIR_DICT[server] + DEFAULT_CONF_FILENAME, "r") as fin:
            conf_string = fin.read()
        double, conf_dict = iscpy.ParseISCString(conf_string)

        print json.dumps(conf_dict, default=lambda o: o.__dict_, indent=4)

        for key in conf_dict:
            if "zone" in key:
                zone_name = re.search(r'"(.*)"', key).group(1)
                local_file_name = conf_dict[key]['file']

                if REMOTE_CONF_DIR in local_file_name:
                    local_file_name = local_file_name.replace(REMOTE_CONF_DIR, LOCAL_DIR_DICT[server])
                if local_file_name[0] == '/':
                    local_file_name = LOCAL_DIR_DICT[server] + local_file_name
                FILE_LOCATION[zone_name] = local_file_name.replace('"', '')

                ZONE_DICT[server].append(zone_name)


def restart_bind(serverhostname):
    #subprocess.call(["ssh", USER_DICT[serverhostname] + "@" + serverhostname, "systemctl restart named"])
    print serverhostname

def find_server(zone_name):
    for server in ZONE_DICT:
        if zone_name in ZONE_DICT[server]:
            return server


# get_all_zone()
FILE_LOCATION['gdn.lokal'] = 'D:/heronimus/dnsapi/zone_gdn.lokal'
FILE_LOCATION['10.17.172.in-addr.arpa'] = 'D:/heronimus/dnsapi/ptr_gdn.lokal'
ZONE_DICT['10.0.2.11'].append('gdn.lokal')
ZONE_DICT['10.0.2.11'].append('10.17.172.in-addr.arpa')
print FILE_LOCATION
print ZONE_DICT
# masukin dia dimana aja, ubah ke direktori absolut di server ini
# kasih format FILE_LOCATION['zone_name'] = "/path/to/file"
