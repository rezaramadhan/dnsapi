"""Setting for file and server locations."""

import logging
import iscpy
import re
logger = logging.getLogger(__name__)

# You may need to change these variables
REMOTE_MNT_DIR = "/"
DEFAULT_CONF_DIR = 'etc/'
DEFAULT_CONF_FILENAME = DEFAULT_CONF_DIR + "named.conf"
SERVER_LIST = ["10.0.2.11", "10.0.2.1"]

USER_DICT = {
    SERVER_LIST[0]: "root",
    SERVER_LIST[1]: "root"
}

LOCAL_MNT_DIR = {
    SERVER_LIST[0]: "/mnt/nfs-dns-coba1/",
    SERVER_LIST[1]: "/mnt/nfs-dns-coba2/"
}

SSH_PORT = 22

# You must not change this variable
IGNORED_ZONE = ['localhost', 'localhost.localdomain', '0.in-addr.arpa',
                '1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.ip6.arpa',
                '1.0.0.127.in-addr.arpa']
logger.debug("Init var")
ZONE_DICT = {}
FILE_LOCATION = {}
ZONE_MNT_DIR = {}
logger.debug("done init var")


def init_data():
    """Initialize all data required in a server."""
    global FILE_LOCATION, ZONE_DICT
    FILE_LOCATION = {}

    for server in SERVER_LIST:
        ZONE_DICT[server] = []
        get_zone(server, LOCAL_MNT_DIR[server] + DEFAULT_CONF_FILENAME)


def get_local_filename(remote_filename, relative_remote_dir, local_mnt_dir):
    """Get the mounted local filename."""
    remote_filename = remote_filename.strip('"')
    if (remote_filename[0] != '/'):
        remote_filename = relative_remote_dir + remote_filename

    local_filename = remote_filename.replace(REMOTE_MNT_DIR, local_mnt_dir, 1)

    return local_filename


def get_zone(server, conf_filename, relative_remote_dir='/etc/'):
    """Read DEFAULT_CONF_FILENAME and parse the config file.

    This method will read all zonefile to get every zonefile available and
    also assign ZONE_DICT which server has a certain zonefile.
    """
    global ZONE_MNT_DIR, FILE_LOCATION, ZONE_DICT
    logger.debug('get_zone on: ' + server + ' ' + conf_filename + ' ' + relative_remote_dir)
    with open(conf_filename, "r") as fin:
        conf_dict, abcd = iscpy.ParseISCString(fin.read())

    try:
        bind_working_dir = conf_dict['options']['directory'].strip('"') + '/'
    except KeyError:
        bind_working_dir = relative_remote_dir
    ZONE_MNT_DIR[server] = bind_working_dir

    for key in conf_dict:
        if (("zone" in key) and ("master" in conf_dict[key]['type'])):
            zone_name = re.search(r'"(.*)"', key).group(1)

            if zone_name not in IGNORED_ZONE:
                FILE_LOCATION[zone_name] = get_local_filename(conf_dict[key]['file'],
                                                              bind_working_dir,
                                                              LOCAL_MNT_DIR[server])
                ZONE_DICT[server].append(zone_name)
        elif ("include" in key):
            # logger.log("get include :" + strconf_dict['include'])
            for (_, value) in conf_dict['include'].items():
                local_filename = get_local_filename(value, bind_working_dir,
                                                    LOCAL_MNT_DIR[server])
                logger.debug("reading include on: " + value + "\nworking dir:" +
                             bind_working_dir)
                get_zone(server, local_filename, bind_working_dir)

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
logger.debug("ZONE_MNT_DIR: " + str(ZONE_MNT_DIR))
