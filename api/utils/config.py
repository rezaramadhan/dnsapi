"""Setting for file and server locations."""

import logging

logger = logging.getLogger(__name__)

# You may need to change these variables
REMOTE_MNT_DIR = "/"
DEFAULT_CONF_DIR = 'etc/'
DEFAULT_CONF_FILENAME = DEFAULT_CONF_DIR + "named.conf"
SERVER_LIST = ["10.0.2.11", "10.0.2.6"]

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
ZONE_DICT = {}
FILE_LOCATION = {}
ZONE_MNT_DIR = {}
