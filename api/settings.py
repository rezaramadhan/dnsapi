"""Setting for file and server locations."""
# server DICT, tuple hostname, username, sama nama zone.
# login ssh via public keys
import iscpy
import json
import re
import subprocess
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

# You must not change this variable
IGNORED_ZONE = ['localhost', 'localhost.localdomain', '0.in-addr.arpa',
                '1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.ip6.arpa',
                '1.0.0.127.in-addr.arpa']
ZONE_DICT = {}
FILE_LOCATION = {}


def init_data():
    """Initialize all data required in a server."""
    global ZONE_DICT, FILE_LOCATION

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
    logger.debug('get_zone on: ' + server + ' ' + conf_filename + ' ' + relative_remote_dir)
    with open(conf_filename, "r") as fin:
        conf_dict, abcd = iscpy.ParseISCString(fin.read())



    try:
        bind_working_dir = conf_dict['options']['directory'].strip('"') + '/'
    except KeyError:
        bind_working_dir = relative_remote_dir

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


def restart_bind(serverhostname):
    """Restart bind on a certain server."""
    check_conf(serverhostname)
    for zone in ZONE_DICT[serverhostname]:
        check_zone(zone)

    p = subprocess.Popen(["ssh", USER_DICT[serverhostname] + "@" + serverhostname,
                          "systemctl restart named"], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    stdout_str, stderr_str = p.communicate()
    if p.returncode != 0:
        raise EnvironmentError('Unable to restart named: ' + str(stderr_str.strip('\n').strip('\r')))


def find_server(zone_name):
    """Find which server has a certain zone."""
    for server in ZONE_DICT:
        if zone_name in ZONE_DICT[server]:
            return server


def check_conf(serverhostname):
    """Check whether the named configuration is valid, raise EnvironmentError otherwise."""
    remote_cmd = "named-checkconf " + REMOTE_MNT_DIR + DEFAULT_CONF_FILENAME
    logger.debug('check_conf, cmd: ' + remote_cmd)

    p = subprocess.Popen(["ssh", USER_DICT[serverhostname] + "@" + serverhostname,
                          remote_cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_str, stderr_str = p.communicate()
    if p.returncode != 0:
        # Restore named (check_conf failed)
        backup_restore_file('restore','named',serverhostname,'.bak')
        # logger.error("Failed to restart named: " + str(stderr_str))
        raise EnvironmentError('Check-conf failed: ' + str(stderr_str.strip('\n').strip('\r')))


def check_zone(zone_name):
    """Check whether a zonefile is valid, raise EnvironmentError otherwise."""
    server = find_server(zone_name)
    remote_cmd = ("named-checkzone " + zone_name + " " +
                  FILE_LOCATION[zone_name].replace(LOCAL_MNT_DIR[server], REMOTE_MNT_DIR))
    logger.debug('check_zone, cmd: ' + remote_cmd)

    p = subprocess.Popen(["ssh", USER_DICT[server] + "@" + server, remote_cmd],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_str, stderr_str = p.communicate()
    if p.returncode != 0:
        # Restore zone (check_zone failed)
	    backup_restore_file('restore','zone',zone_name,'.bak')
        # logger.error("Failed to restart named: " + str(stderr_str))
        raise EnvironmentError('Check-zone failed: ' + str(stderr_str.strip('\n').strip('\r')))

def backup_restore_file(action, file_type, origin, format_backup):
    """ Backup/Restore Bind configuration (named.conf) or Zones File.
        - action parameter can be either 'backup' or 'restore',
        - file_type parameter can be either 'zone' or 'named',
        - origin is either server name / zone name,
        - format_backup is backup file extensions.
    """
    logger.info("backup_restore_file: " + action + " - " + file_type +
        " - " + origin + " - " + format_backup)
    if action == 'backup' :
        if (file_type == 'zone'):
            file_src = FILE_LOCATION[origin]
            file_dst = file_src+format_backup
        if (file_type == 'named'):
            file_src = LOCAL_MNT_DIR[origin] + DEFAULT_CONF_FILENAME
            file_dst = file_src+format_backup
    if action == 'restore':
        if (file_type == 'zone'):
            file_dst = FILE_LOCATION[origin]
            file_src = file_dst+format_backup
        if (file_type == 'named'):
            file_dst = LOCAL_MNT_DIR[origin] + DEFAULT_CONF_FILENAME
            file_src = file_dst+format_backup

    copyfile(file_src, file_dst)

init_data()
# FILE_LOCATION['gdn.lokal'] = '~/haha'

# FILE_LOCATION['gdn.lokal'] = '/home/linux1-user/dnsapi/zone_gdn.lokal'
# FILE_LOCATION['10.17.172.in-addr.arpa'] = '/home/linux1-user/dnsapi/ptr_gdn.lokal'
# ZONE_DICT['10.0.2.11'].append('gdn.lokal')
# ZONE_DICT['10.0.2.11'].append('10.17.172.in-addr.arpa')
logger.debug('FILE_LOCATION: ' + str(FILE_LOCATION))
logger.debug('ZONE_DICT: ' + str(ZONE_DICT))
