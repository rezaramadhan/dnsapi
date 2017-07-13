"""This module handle a DNS Zone management."""

import re

RCLASS_LIST = ['IN', 'CH']
RTYPE_LIST = ['A', 'AAAA', 'MX', 'NS', 'PTR', 'CNAME', 'SOA', 'URI', 'TXT']


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

    def __init__(self, name="", ttl="", rclass="", rtype="", rdata=""):
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


class MXRecordData(RecordData):
    """MXRecordData class.

    A record data class for MX Record, has two attribute; priority and address.
    """

    def __repr__(self):
        """Change class to string, each attribute is separated by a tab."""
        return self.priority + "\t" + self.address

    def parse_rdata(self, tokens=None, file_lines=None):
        """Parse rdata from the given tokens.

        Priority is the first token and address is the last token.
        """
        self.priority = tokens[0]
        self.address = tokens[1]
        # file_lines.pop(0)


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
        for record in self.resource_records:
            str_repr += str(record) + "\n"
        return str_repr

    def __str__(self):
        """Change class to string."""
        return self.__repr__()

    def find_record(self, name):
        """Find a record with the given name.

        return None if record not exist.
        """
        for record in self.resource_records:
            if (record.name == name):
                return record
        return None

    def increment_soa(self):
        """Increment a SOA's serial number by 1."""
        for record in self.resource_records:
            if (record.rtype == "SOA"):
                break

        record.rdata.serial_no = int(record.rdata.serial_no) + 1

    def delete_record(self, name):
        """Delete a record that has a certain name.

        Does nothing if record doesn't exist.
        """
        try:
            self.resource_records.remove(self.find_record(name))
            self.increment_soa()
        except:
            pass

    def add_record(self, record):
        """Add a record to a Zone resource records."""
        self.resource_records.append(record)
        self.increment_soa()

    def update_record(self, name, new_record):
        """Update a record that has a certain name.

        Does nothing if record doesn't exist.
        """
        try:
            record_idx = self.resource_records.index(self.find_record(name))
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

            record = DNSResourceRecord(name=tokens[0])

            for i in range(1, len(tokens)):
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

        # print zonefile_lines
        self.directives = self.parse_directives(zonefile_lines)

        self.resource_records = self.parse_records(zonefile_lines)
