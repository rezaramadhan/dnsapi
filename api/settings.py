"""Setting for file and server locations."""
# server DICT, tuple hostname, username, sama nama zone.
# login ssh via public keys
import iscpy
import json
import re
import subprocess
import logging

DEFAULT_CONF_FILENAME = "named.conf.local"
REMOTE_CONF_DIR = "/etc/named/"
SERVER_LIST = ["10.0.2.11", "10.0.2.6"]

USER_DICT = {
    SERVER_LIST[0]: "root",
    SERVER_LIST[1]: "root"
}

LOCAL_DIR_DICT = {
    SERVER_LIST[0]: "/mnt/nfs-dns-coba1/",
    SERVER_LIST[1]: "/mnt/nfs-dns-coba2/"
}

ZONE_DICT = {}
FILE_LOCATION = {}

logger = logging.getLogger(__name__)


def init_data():
    """Initialize all data required in a server."""
    global ZONE_DICT, FILE_LOCATION

    for server in SERVER_LIST:
        ZONE_DICT[server] = []
    FILE_LOCATION = {}

    get_all_zone()


def get_all_zone():
    """Read DEFAULT_CONF_FILENAME and parse the config file.

    This method will read all zonefile to get every zonefile available and
    also assign ZONE_DICT which server has a certain zonefile.
    """
    for server in LOCAL_DIR_DICT:
        with open(LOCAL_DIR_DICT[server] + DEFAULT_CONF_FILENAME, "r") as fin:
            conf_string = fin.read()
        conf_dict, abcd = iscpy.ParseISCString(conf_string)

        logger.debug("CONF_DICT: " +
                     json.dumps(conf_dict, default=lambda o: o.__dict_, indent=4))

        for key in conf_dict:
            if "zone" in key:
                zone_name = re.search(r'"(.*)"', key).group(1)
                local_file_name = conf_dict[key]['file']

                if REMOTE_CONF_DIR in local_file_name:
                    local_file_name = local_file_name.replace(REMOTE_CONF_DIR,
                                                              LOCAL_DIR_DICT[server])

                if local_file_name[0] == '/':
                    local_file_name = LOCAL_DIR_DICT[server] + local_file_name
                FILE_LOCATION[zone_name] = local_file_name.replace('"', '')

                ZONE_DICT[server].append(zone_name)


def restart_bind(serverhostname):
    """Restart bind on a certain server."""
    result = subprocess.call(["ssh", USER_DICT[serverhostname] + "@" +
                              serverhostname, "systemctl restart named"])
    if result != 0:
        logger.error("Failed to restart named: " + str(result))
        raise EnvironmentError('Unable to restart named')


def find_server(zone_name):
    """Find which server has a certain zone."""
    for server in ZONE_DICT:
        if zone_name in ZONE_DICT[server]:
            return server


init_data()
# FILE_LOCATION['gdn.lokal'] = '~/haha'

# FILE_LOCATION['gdn.lokal'] = '/home/linux1-user/dnsapi/zone_gdn.lokal'
# FILE_LOCATION['10.17.172.in-addr.arpa'] = '/home/linux1-user/dnsapi/ptr_gdn.lokal'
# ZONE_DICT['10.0.2.11'].append('gdn.lokal')
# ZONE_DICT['10.0.2.11'].append('10.17.172.in-addr.arpa')
logger.debug('FILE_LOCATION: ' + str(FILE_LOCATION))
logger.debug('ZONE_DICT: ' + str(ZONE_DICT))
