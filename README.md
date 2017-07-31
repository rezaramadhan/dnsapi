# dnsapi

## Description
__dnsapi__ provides API to retrieve and modify BIND files. Return formats of all endpoints is in JSON.

## API Usage
If you want to see the API documentation, you may see the [following file](API.md)

## Requirements
#### rpm/deb package
*   httpd/apache2
*   mod_wsgi
*   python2
*   python-pip
*   ssh
*   ssfs/nfs client

#### Python Package
*   iscpy
*   django
*   requests

## Installation & Setup
#### Download source code
Download the `dnsapi` source code and `iscpy_modified`. Currently, `dnsapi` located on <https://github.com/rezaramadhan/dnsapi.git> and `iscpy_modified` is on <https://github.com/utamid/iscpy_modified.git>

Place `dnsapi` on any path, and `iscpy_modified/iscpy` on
`/usr/lib/python2.7/site-packages/`

#### Install required packages
dnsapi needs the following package on CentOS:
> httpd
> mod_wsgi
> python2
> python-pip
> ssh

Also install the following pip package
> django
> requests

#### Setup httpd
Refer to this tutorial: <https://www.digitalocean.com/community/tutorials/how-to-serve-django-applications-with-apache-and-mod_wsgi-on-centos-7>


To make things easier, you may change the default user httpd runs inside  httpd config. The file can be found on: `/etc/httpd/conf/httpd.conf`


Don't forget to restart httpd after finishing this section, obviously.

#### Mount remote directory
You can use `nfs`, `sshfs`, or any other way to mount the remote Mount the remote directory on any path you want. Write down the path so you don't forget it; you may call it `LOCAL_MNT_DIR` to make it memorable.

#### Setup ssh keys between the DNS server and this server
Refer to this tutorial: <https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys--2>

Make sure that the DNS server's user has read & write access on bind configuration and all zone file. This user also need to be able to use `sudo` without any password prompt.

#### Setup `api/settings.py`
There are a few variables value you need to change on `dnsapi` source code depends on your server configuration. Those are:

*   `DEFAULT_CONF_DIR` The absolute path of bind configuration file __without__ the forward slash at the beggining (e.g. `/etc/` will become `etc/`)

*   `DEFAULT_CONF_FILENAME` The default configuration file of bind name, usually `named.conf`

*   `REMOTE_MNT_DIR` The remote directory that is being mounted on this server. As an example, if you mount `/etc/named/` on this server as `/mnt/dns1/`, you need to put `/etc/named/` as this variable value.

*   `SERVER_LIST` The list of the DNS server hostname/ip

*   `USER_DICT` A dictionary that contain the username that we use to ssh to a remote DNS server. Use the following format:
    ```
    USER_DICT = {
        SERVER_LIST[0]: "user1",
        SERVER_LIST[1]: "user2"
    }
    ```

*   `LOCAL_MNT_DIR` A path where you mount the remote directory on this server. As an example, if you mount `/etc/named/` on this server as `/mnt/dns1/`, you need to put `/mnt/dns1/` as this variable value. Use the following format:
    ```
    LOCAL_MNT_DIR = {
        SERVER_LIST[0]: "/mnt/dns1/",
        SERVER_LIST[1]: "/mnt/dns2/"
    }
    ```

The default source code already gives some example of the value needed; you can imitate the given value as needed.


#### Configure Permission & Firewall
Make sure that the user that run httpd has write permission on `dnsapi/*` as it needs to write the application log and to create socket that `dnsapi/wsgi.py` need to communicate with httpd. You may also need to configure SELinux according to your need.

dnsapi runs on `http`, so allow it on your firewall. If you want, you can also configure it to run on `https` and allow `https` on your firewall.

## Introduction to the log file
dnsapi produce the log on `log/` directory. The files produced are:

1.  `access.log` This is the access file produced by dnsapi, contained the POST/GET/PUT/DELETE request sent by the client and the status code response given to each request.

1.  `api.log` This shows any logging given by the API. you can edit the debug level on `dnsapi/settings` on the loggers section.

1.  `webui.log` This shows any logging given by the API. you can edit the debug level on `dnsapi/settings` on the loggers section.

1.  `error.log` This produces any error that isn't handled by _api.log_ and _error.log_, usually error caused by django package.

If the following error doesn't solve your issue, you may need to see the httpd's log on `/var/log/httpd/`

## How it works: Populating `dnsapi/settings.py` variable

This section will describe how __dsnapi__ works. How it get all required data, how it modified a zone file and bind configuration file, and how it restart bind on a remote server.

1.  Parse bind config using iscpy_modified.

    Using the `LOCAL_MNT_DIR` and `DEFAULT_CONF_FILENAME` inside `api/settings.py`, __dsnapi__ can locate the locally mounted bind configuration file. It can parse the config file using iscpy and gives the parsed result as a dictionary.

1.  Find all available zone in the server.

    The program will then get `directory` section in the `option` statement within the dictionary to get bind's working directory. Then, it will find all master zone and populate `FILE_LOCATION` and `ZONE_DICT` variable `within dnsapi/settings.py`

## How it works: Modifying a zone
1.  Parse configuration file

    Using the same method as the previous section, __dsnapi__ will read the bind configuration file and convert it to a dictionary.

1.  Backup the current file

    Before it make any changes to the configuration file, __dsnapi__ will make a copy of the working configuration file inside the same directory.

1.  Create new zone statement and a new zone file

    The modified version of `iscpy` provides a method to create a new zone statement within the dictionary. This modified dictionary will be written to the bind configuration file. Please note that any comment in the previous configuration file will be deleted.

    If needed, __dsnapi__ will create a new zone file with the provided directives, SOA record, and NS record.

1.  Restart bind

    Before restarting bind, __dsnapi__ make sure that the modified configuration file is valid and all zone within the configuration file has a valid zone file using `named-checkconf` and `named-checkzone` provided by `bind` package.

    If any of the checks failed, __dsnapi__ will revert the configuration and zone file to the previous version avaiable.


## How it works: Modifying a record
1.  Parse zone

    __dsnapi__ uses `FILE_LOCATION` variable in `api/settings.py` to get the file containing a zone given a certain zone name; after that, it will read the file and parse it using `api/dns.py`.

    The parsing process and the internal data structure will be explained on the next section.

1.  Backup the current file

    As usual, __dsnapi__ will backup the zonefile before it makes any changes.

1.  Modify the record

    __dsnapi__ will modify the internal data, which is the resource_records attribute within the DNSZone class when it needs to create a new record, deleting a record, reading a record, or updating a new record.

    After it make any changes, it will write the internal data to the appropriate zone file.

1.  Restart bind

    This process basically works as if restarting bind when you modify a zone.

## Introduction to the zone parser (`api/dns.py`)
### Internal data structure

### Parsing method
