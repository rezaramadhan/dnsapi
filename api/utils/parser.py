"""This module handle a DNS Zone management."""

import re
import json
import logging

logger = logging.getLogger(__name__)
RCLASS_LIST = ['IN', 'CH']
RTYPE_LIST = ['A', 'AAAA', 'MX', 'NS', 'PTR', 'CNAME', 'SOA', 'URI', 'TXT']


class RecordData():
    """RecordData class.

    A Generic class for a record type that only has a single data. Such as A,
    AAAA, CNAME, PTR, TXT, NS
    """

    def __init__(self, address=""):
        """Public constructor."""
        self.address = address

    def __repr__(self):
        """Change class to string, each attribute is separated by a tab."""
        return self.address

    def __str__(self):
        """Change class to string, each attribute is separated by a tab."""
        return self.__repr__()

    def parse_rdata(self, tokens=None, file_lines=None):
        """Parse rdata from the given tokens."""
        self.address = tokens[0]
        # file_lines.pop(0)

    def is_equal_to(self, dict):
        """Check if my data is equal to dict"""
        logger.debug(self.address + ' ' + dict['address'])
        return self.address == dict['address']

    def fromJSON(self, json_obj):
        """Public constructor to create class from a json string."""
        self.address = json_obj['address'] if 'address' in json_obj else self.address

    def toJSON(self):
        """Convert class to JSON file."""
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


class MXRecordData(RecordData):
    """MXRecordData class.

    A record data class for MX Record, has two attribute; priority and address.
    """

    def __repr__(self):
        """Change class to string, each attribute is separated by a tab."""
        return self.priority + "\t" + self.address

    def is_equal_to(self, dict):
        """Check if my data is equal to dict"""
        return self.address == dict['address'] and self.priority == dict['priority']

    def parse_rdata(self, tokens=None, file_lines=None):
        """Parse rdata from the given tokens.

        Priority is the first token and address is the last token.
        """
        self.priority = tokens[0]
        self.address = tokens[1]
        # file_lines.pop(0)

    def fromJSON(self, json_obj):
        """Public constructor to create class from a json string."""
        self.priority = json_obj['priority'] if 'priority' in json_obj else self.priority
        self.address = json_obj['address'] if 'address' in json_obj else self.address

class SOARecordData(RecordData):
    """SOARecordData class.

    A record data class for SOA Record. SOA Record consist of the name of the
    authoritative master name server for the zone and the email address of
    someone responsible for management of the name server. The parameters of
    the SOA record also specify a list of timing and expiration parameters
    (serial number, slave refresh period, slave retry time, slave expiration
    time, and the maximum time to cache the record).
    """

    def __init__(self, authoritative_server="", admin_email="", serial_no="",
                 slv_refresh_period="", slv_retry="", slv_expire="",
                 max_time_cache=""):
        """Public constructor."""
        self.authoritative_server = authoritative_server
        self.admin_email = admin_email
        self.serial_no = serial_no
        self.slv_refresh_period = slv_refresh_period
        self.slv_retry = slv_retry
        self.slv_expire = slv_expire
        self.max_time_cache = max_time_cache

    def __repr__(self):
        """Change class to string.

        This method outputs the following format:
        name-server email-addr  (   sn
                                ref
                                ret
                                ex
                                min )
        """
        str_repr = ""
        str_repr += self.authoritative_server + "\t"
        str_repr += self.admin_email + "\t" + "("
        str_repr += "\t" + str(self.serial_no) + "\n"
        str_repr += "\t\t\t\t\t\t" + self.slv_refresh_period + "\n"
        str_repr += "\t\t\t\t\t\t" + self.slv_retry + "\n"
        str_repr += "\t\t\t\t\t\t" + self.slv_expire + "\n"
        str_repr += "\t\t\t\t\t\t" + self.max_time_cache + "\t" ")"
        return str_repr

    def parse_rdata(self, tokens=None, file_lines=None):
        """Parse rdata from the given tokens.

        This method assume SOA is in this format:
        name-server email-addr  (   sn
                                ref
                                ret
                                ex
                                min )
        """
        self.authoritative_server = tokens[0]
        self.admin_email = tokens[1]

        soa_tokens = []
        try:
            soa_tokens.append(tokens[tokens.index("(") + 1])
        except:
            pass

        tokens = []
        while not(")" in tokens):
            soa_tokens += tokens
            file_lines.pop(0)
            tokens = re.split('[ \t]*', file_lines[0])
            tokens = list(filter(None, tokens))
        soa_tokens += tokens[:tokens.index(")")]

        # file_lines.pop(0)
        self.serial_no = soa_tokens[0]
        self.slv_refresh_period = soa_tokens[1]
        self.slv_retry = soa_tokens[2]
        self.slv_expire = soa_tokens[3]
        self.max_time_cache = soa_tokens[4]

    def fromJSON(self, json_obj):
        """Public constructor to create class from a json string."""
        self.admin_email = json_obj['admin_email'] if 'admin_email' in json_obj else self.admin_email
        self.authoritative_server = json_obj['authoritative_server'] if 'authoritative_server' in json_obj else self.authoritative_server
        self.serial_no = json_obj['serial_no'] if 'serial_no' in json_obj else self.serial_no
        self.slv_refresh_period = json_obj['slv_refresh_period'] if 'slv_refresh_period' in json_obj else self.slv_refresh_period
        self.slv_retry = json_obj['slv_retry'] if 'slv_retry' in json_obj else self.slv_retry
        self.slv_expire = json_obj['slv_expire'] if 'slv_expire' in json_obj else self.slv_expire
        self.max_time_cache = json_obj['max_time_cache'] if 'max_time_cache' in json_obj else self.max_time_cache

    def is_equal_to(self, dict):
        """Check if my data is equal to dict."""
        return (self.admin_email == dict['address'] and self.authoritative_server == dict['priority'] and
                self.serial_no == dict['serial_no'] and self.slv_refresh_period == dict['slv_refresh_period'] and
                self.slv_retry == dict['slv_retry'] and self.max_time_cache == dict['max_time_cache'])

class DNSResourceRecord():
    """DNSResourceRecord class.

    A class that handles a single resource record in a DNS Zone, usually
    a resource record described in one line within DNS Zone file.
    The description consists of several fields separated by white space
    (spaces or tabs) as follows:
    name  |  ttl  |  record class  |  record type  |  record data

    note that ttl and record class' order might be exchanged
    references: https://en.wikipedia.org/wiki/Zone_file

    @ivar name: a resource record name, the first field in the line
    @type name: string
    @ivar ttl: a resource record ttl, perhaps the second or third field
    @type ttl: string
    @ivar rclass: a resource record class
    @type rclass: string
    @ivar rtype: a resource record type
    @type rtype: string
    @ivar rtype: a resource record data,
                 depend on resource type might have different data
    @type rtype: dns.ResourceData

    @TODO: change ttl to integer, convert on print
    """

    def __init__(self, name="", ttl="", rclass="", rtype="", rdata=RecordData()):
        """Public constructor."""
        self.name = name
        self.ttl = ttl
        self.rclass = rclass
        self.rtype = rtype
        self.rdata = rdata

    def __repr__(self):
        """Change class to string, each attribute is separated by a tab."""
        str_repr = self.name
        if self.rclass:
            str_repr += "\t" + self.rclass
        if self.ttl:
            str_repr += "\t" + self.ttl
        if self.rtype:
            str_repr += "\t" + self.rtype
        str_repr += "\t" + str(self.rdata)
        return str_repr

    def __str__(self):
        """Change class to string, each attribute is separated by a tab."""
        return self.__repr__()

    def toJSON(self):
        """Convert class to JSON file."""
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def fromJSON(self, json_obj):
        """Public constructor to create class from a json string."""
        self.name = json_obj['name'] if 'name' in json_obj else self.name
        self.ttl = json_obj['ttl'] if 'ttl' in json_obj else self.ttl
        self.rclass = json_obj['rclass'] if 'rclass' in json_obj else self.rclass
        self.rtype = json_obj['rtype'] if 'rtype' in json_obj else self.rtype
        if 'rdata' in json_obj:
            self.rdata.fromJSON(json_obj['rdata'])


class DNSZone():
    """DNSZone class.

    This class is a representation of DNS Zone file. A DNS Zone contain some
    DNS Directives on the start and followed by a list of DNS Resource Records
    """

    def __init__(self, directives=None, resource_records=None):
        """Public constructor."""
        self.directives = directives
        self.resource_records = resource_records

    def __repr__(self):
        """Change class to string.

        This method produces a string with the following format:
        $directive1 directive1value
        $directive2 directive2value
        .
        .
        name	ttl	record class	record type	record data
        """
        str_repr = ""
        for key in self.directives:
            str_repr += "$" + key + " " + self.directives[key] + "\n"

        prev_record = DNSResourceRecord()
        for record in self.resource_records:
            if (record.name == prev_record.name):
                str_repr += re.sub('^\S*', '', str(record)) + "\n"
            else:
                str_repr += str(record) + "\n"
            prev_record = record
        return str_repr

    def __str__(self):
        """Change class to string."""
        return self.__repr__()

    def find_record(self, name, rclass=None, rtype=None, rdata=None):
        """Find a record with the given name.

        raise LookupError when record is not found
        """
        logger.debug('Finding:' + name + " " + str(rdata))
        for record in self.resource_records:
            # continue to next loop if X is not empty and X does not equal record.X
            if rclass and rclass != record.rclass:
                continue
            if rtype and rtype != record.rtype:
                continue
            if rdata and not record.rdata.is_equal_to(rdata):
                continue
            if (record.name == name):
                logger.debug('Found: ' + str(record))
                return record
        raise LookupError("Record not found")

    def increment_soa(self):
        """Increment a SOA's serial number by 1."""
        for record in self.resource_records:
            if (record.rtype == "SOA"):
                break

        record.rdata.serial_no = int(record.rdata.serial_no) + 1

    def delete_record(self, name, rclass=None, rtype=None, rdata=None):
        """Delete a record that has a certain name.

        Does nothing if record doesn't exist.
        """
        try:
            self.resource_records.remove(self.find_record(name, rclass, rtype, rdata))
            logger.debug('Deleted ' + name + " " + str(rdata))

            self.increment_soa()
        except:
            pass

    def add_record(self, record):
        """Add a record to a Zone resource records."""
        self.resource_records.append(record)
        self.increment_soa()

    def update_record(self, name, new_record, rclass=None, rtype=None, rdata=None):
        """Update a record that has a certain name.

        Does nothing if record doesn't exist.
        """
        try:
            record_idx = self.resource_records.index(self.find_record(name, rclass, rtype, rdata))
            self.resource_records[record_idx] = new_record
            self.increment_soa()
        except:
            pass

    def write_to_file(self, filename):
        """Write the string representation to a file."""
        with open(filename, "w") as fout:
            isi = self.__repr__()
            fout.write(isi)

    def is_token_ttl(self, token):
        """Check wether a token is a valid TTL."""
        pattern = re.compile("^\d*[hHdDwWmMyY]?$")
        return pattern.match(token)

    def parse_directives(self, zonefile_lines):
        """DNS Directives Parsing, store to a dictionary."""
        directives = {}
        while (zonefile_lines[0][0] == "$"):
            tokens = re.split('[ \t]*', zonefile_lines[0])
            directives[tokens[0][1:]] = tokens[1]
            zonefile_lines.pop(0)
        return directives

    def parse_records(self, zonefile_lines):
        """DNS Record parsing.

        Split each line to a token with whitespace as a delimiter
        """
        records = []
        while (len(zonefile_lines) > 0):
            tokens = re.split('[ \t]*', zonefile_lines[0].rstrip('\n'))

            record = DNSResourceRecord()

            if tokens[0] in RCLASS_LIST or tokens[0] in RTYPE_LIST:
                startidx = 0
            else:
                startidx = 1
                record.name = tokens[0]

            for i in range(startidx, len(tokens)):
                if tokens[i] in RCLASS_LIST:
                    record.rclass = tokens[i]
                elif self.is_token_ttl(tokens[i]):
                    record.ttl = tokens[i]
                elif tokens[i] in RTYPE_LIST:
                    record.rtype = tokens[i]
                    if record.rtype == "MX":
                        record.rdata = MXRecordData()
                    elif record.rtype == "SOA":
                        record.rdata = SOARecordData()
                    else:
                        record.rdata = RecordData()
                    break
                else:
                    raise Exception('Unknown token', tokens[i])

            record.rdata.parse_rdata(tokens[i+1:], zonefile_lines)
            if (record.name == ""):
                record.name = records[-1].name

            zonefile_lines.pop(0)
            records.append(record)

        return records

    def read_from_file(self, filename):
        """Read and parse a file to get a DNS zone file."""
        # Read file, store all line from file to a list of line
        # also strip all line from newline (\n or \r)
        with open(filename, "r") as zonefile:
            zonefile_lines = zonefile.readlines()
            for i in range(0, len(zonefile_lines)):
                zonefile_lines[i] = re.sub('\r?\n', '', zonefile_lines[i])
                zonefile_lines[i] = re.sub(';.*', '', zonefile_lines[i])

        self.directives = self.parse_directives(zonefile_lines)
        self.resource_records = self.parse_records(zonefile_lines)

    def toJSON(self):
        """Convert class to JSON file."""
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
