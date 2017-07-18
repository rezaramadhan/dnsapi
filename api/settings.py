"""Setting for file and server locations."""
# server DICT, tuple hostname, username, sama nama zone.
# login ssh via public keys
import iscpy
import json
import re
DEFAULT_CONF_FILENAME = "named.conf.local"
REMOTE_CONF_DIR = "/etc/named/"
USER_DICT = {"10.0.2.11": "dnsuser", "10.0.2.6": "dnsuser"}
LOCAL_DIR_DICT = {"10.0.2.11": "/mnt/nfs-dns-coba2/",
                  "10.0.2.6": "/mnt/nfs-dns-coba1/"}
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
                FILE_LOCATION[zone_name] = local_file_name
                ZONE_DICT[server].append(zone_name)


get_all_zone()
print FILE_LOCATION
print ZONE_DICT
# masukin dia dimana aja, ubah ke direktori absolut di server ini
# kasih format FILE_LOCATION['zone_name'] = "/path/to/file"
