"""Bind related function."""
from config import (FILE_LOCATION, LOCAL_MNT_DIR, DEFAULT_CONF_FILENAME,
                    REMOTE_MNT_DIR, ZONE_DICT, USER_DICT,SSH_PORT, find_server)
from shutil import copyfile
from excpt import BindError
import subprocess
import logging
import os.path

logger = logging.getLogger(__name__)


def remote_exec(remote_cmd, hostname):
    """Execute remote command on a certain hostname."""
    return subprocess.Popen(["ssh","-p", SSH_PORT, USER_DICT[hostname] + "@" + hostname,
                             remote_cmd], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)


def restart_bind(serverhostname):
    """Restart bind on a certain server."""
    check_conf(serverhostname)
    for zone in ZONE_DICT[serverhostname]:
        check_zone(zone)

    p = remote_exec("systemctl restart named", serverhostname)
    stdout_str, stderr_str = p.communicate()
    if p.returncode != 0:
        msg = 'Unable to restart named: ' + str(stderr_str.strip('\n').strip('\r'))
        file_type = None
        origin = None
        raise BindError({'msg': msg, 'file_type': file_type, 'origin': origin})


def check_conf(serverhostname):
    """Check whether the named configuration is valid, raise EnvironmentError otherwise."""
    remote_cmd = "named-checkconf " + REMOTE_MNT_DIR + DEFAULT_CONF_FILENAME
    logger.debug('check_conf, cmd: ' + remote_cmd)

    p = remote_exec(remote_cmd, serverhostname)
    stdout_str, stderr_str = p.communicate()
    if p.returncode != 0:
        msg = 'Check-conf failed: ' + str(stderr_str.strip('\n').strip('\r'))
        file_type = 'named'
        origin = serverhostname
        raise BindError({'msg': msg, 'file_type': file_type, 'origin': origin})


def check_zone(zone_name):
    """Check whether a zonefile is valid, raise EnvironmentError otherwise."""
    server = find_server(zone_name)
    remote_cmd = ("named-checkzone " + zone_name + " " +
                  FILE_LOCATION[zone_name].replace(LOCAL_MNT_DIR[server], REMOTE_MNT_DIR))
    logger.debug('check_zone, cmd: ' + remote_cmd)

    p = remote_exec(remote_cmd, server)
    stdout_str, stderr_str = p.communicate()
    if p.returncode != 0:
        msg = 'Check-conf failed: ' + str(stderr_str.strip('\n').strip('\r'))
        file_type = 'named'
        origin = zone_name
        raise BindError({'msg': msg, 'file_type': file_type, 'origin': origin})

def backup_restore_file(action, file_type, origin, format_backup):
    """Backup/Restore Bind configuration (named.conf) or Zones File.

    - action parameter can be either 'backup' or 'restore',
    - file_type parameter can be either 'zone' or 'named',
    - origin is either server name / zone name,
    - format_backup is backup file extensions.
    """
    logger.info("backup_restore_file: " + action + " - " + file_type +
                " - " + origin + " - " + format_backup)
    if action == 'backup':
        if (file_type == 'zone'):
            file_src = FILE_LOCATION[origin]
            file_dst = file_src+format_backup
        if (file_type == 'named'):
            file_src = LOCAL_MNT_DIR[origin] + DEFAULT_CONF_FILENAME
            file_dst = file_src+format_backup
    elif action == 'restore':
        if (file_type == 'zone'):
            file_dst = FILE_LOCATION[origin]
            file_src = file_dst+format_backup
        if (file_type == 'named'):
            file_dst = LOCAL_MNT_DIR[origin] + DEFAULT_CONF_FILENAME
            file_src = file_dst+format_backup

    if (os.path.isfile(file_src)):
        copyfile(file_src, file_dst)
