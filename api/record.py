"""Class-based view for record handling."""
import json
import logging

from django.views.generic import View
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from dns import (DNSZone, RecordData, MXRecordData, SOARecordData,
                 DNSResourceRecord)
from settings import FILE_LOCATION, restart_bind, find_server

# logger = logging.getLogger("django")

def find_reverse_zone(address):
    """Return the reverse zone origin given a certain address."""
    reverse_addr = address.split('.')[:3][::-1]
    return '.'.join(reverse_addr) + ".in-addr.arpa"


def reverse_record_add(name, origin_zone, address, ttl=""):
    """Add the associated reverse zone according to the address given."""
    reverse_zone_origin = find_reverse_zone(address)

    if not (reverse_zone_origin in FILE_LOCATION):
        raise KeyError("Invalid Reverse Zone: " + reverse_zone_origin)

    reverse_zone = DNSZone()
    reverse_zone.read_from_file(FILE_LOCATION[reverse_zone_origin])
    reverse_record = DNSResourceRecord()
    reverse_record.name = address.split('.')[3]
    reverse_record.ttl = ttl
    reverse_record.rclass = "IN"
    reverse_record.rtype = "PTR"
    reverse_record.rdata.address = name + '.' + origin_zone + '.'
    reverse_zone.add_record(reverse_record)
    reverse_zone.write_to_file(FILE_LOCATION[reverse_zone_origin])
    restart_bind(find_server(reverse_zone_origin))


def reverse_record_delete(name, address):
    """Delete the associated reverse zone according to the address given."""
    reverse_zone_origin = find_reverse_zone(address)

    if not (reverse_zone_origin in FILE_LOCATION):
        raise KeyError("Invalid Reverse Zone: " + reverse_zone_origin)

    reverse_zone = DNSZone()
    reverse_zone.read_from_file(FILE_LOCATION[reverse_zone_origin])
    reverse_zone.delete_record(address.split('.')[3])
    reverse_zone.write_to_file(FILE_LOCATION[reverse_zone_origin])

    restart_bind(find_server(reverse_zone_origin))


@method_decorator(csrf_exempt, name='dispatch')
class RecordView(View):
    """RecordView, a generic class-based-view.

    This method serve:
        GET to retrieve information about NS record
        PUT to update a NS record
        DELETE to delete a NS record
    """

    http_method_names = ['get', 'put', 'delete', 'post']

    def get(self, request, zone_origin, record_name):
        """GET Method handler, used to retrieve all information about a record.

        This endpoint recieve the following JSON data as an optional search
        arguments
        {
            "rclass" : "record_rclass",
            "rtype" : "record_rtype",
            "rdata" : {
                "rdata_name1" : "data",
                ...
            },
        }
        This endpoint will return the following JSON file:
        {
            "name" : "record_name",
            "rclass" : "record_rclass",
            "ttl" : "record_ttl",
            "rtype" : "record_rtype",
            "rdata" : {
                "rdata_name1" : "data",
                ...
            },
        }

        And return {"status" : "notfound"} if the record file is not exist
        """
        # logger.info("get item:" + record_name)
        try:
            if request.body.decode('utf-8'):
                payload = json.loads(request.body.decode('utf-8'))
                rclass = payload.get("rclass")
                rtype = payload.get("rtype")
                rdata = payload.get("rdata")
            else:
                rclass = rtype = rdata = None

            if not (zone_origin in FILE_LOCATION):
                raise KeyError('Invalid Zone: ' + zone_origin)

            zone = DNSZone()
            zone.read_from_file(FILE_LOCATION[zone_origin])
            record = zone.find_record(record_name, rclass, rtype, rdata)
            # logger.info("get item:" + record_name)
            # print logger
            return HttpResponse(record.toJSON() if record
                                else '{"status" : "notfound"}')
        except ValueError:
            return HttpResponse('{"status" : "Invalid JSON arguments"}')
        except KeyError as k_err:
            return HttpResponse('{"status" : "'+k_err.args[0]+'"}')
        except LookupError as l_err:
            return HttpResponse('{"status" : "'+l_err.args[0]+'"}')

    def delete(self, request, zone_origin, record_name):
        """DELETW Method handler, used to delete a record.

        This endpoint recieve no JSON data. If there's any, it will be ignored.
        {
            "rclass" : "record_rclass",
            "rtype" : "record_rtype",
            "rdata" : {
                "rdata_name1" : "data",
                ...
            },
        }
        This endpoint will return { "status" : "ok" } if deleting a record is
        successfull and {"status" : "failed"} otherwise

        @TODO: Handle kalo ga nemu
        """
        # handle the post request
        try:
            if request.body.decode('utf-8'):
                payload = json.loads(request.body.decode('utf-8'))
                rclass = payload.get("rclass")
                rtype = payload.get("rtype")
                rdata = payload.get("rdata")
            else:
                rclass = rtype = rdata = None

            if not (zone_origin in FILE_LOCATION):
                raise KeyError('Invalid Zone: ' + zone_origin)

            zone = DNSZone()
            zone.read_from_file(FILE_LOCATION[zone_origin])
            deleted_record = zone.find_record(record_name, rclass, rtype, rdata)
            zone.delete_record(record_name, rclass, rtype, rdata)
            print zone
            zone.write_to_file(FILE_LOCATION[zone_origin])

            if deleted_record.rtype == "A" or deleted_record.rtype == "MX":
                reverse_record_delete(deleted_record.name, deleted_record.rdata.address)

            restart_bind(find_server(zone_origin))
            return HttpResponse('{"status" : "ok"}')
        except ValueError:
            return HttpResponse('{"status" : "Invalid JSON arguments"}')
        except KeyError as k_err:
            return HttpResponse('{"status" : "'+k_err.args[0]+'"}')
        except LookupError as l_err:
            return HttpResponse('{"status" : "'+l_err.args[0]+'"}')

    def put(self, request, zone_origin, record_name):
        """GET Method handler, used to update a record.

        This endpoint recieve the following JSON file:
        {
            "rclass" : "record_rclass",
            "ttl" : "record_ttl",
            "rtype" : "record_rtype",
            "rdata" : {
                "rdata_name1" : "data",
                ...
            },
        }
        Note that all field is optional. You only need to use it if you want to
        update the value.

        This endpoint will return { "status" : "ok" } if updating a record is
        successfull and {"status" : "fail"} otherwise
        """
        try:
            payload = json.loads(request.body.decode('utf-8'))

            if not (zone_origin in FILE_LOCATION):
                raise KeyError('Invalid Zone: ' + zone_origin)

            zone = DNSZone()
            zone.read_from_file(FILE_LOCATION[zone_origin])
            record = zone.find_record(record_name)

            # delete old reverse record
            if (record.rtype == "A" or record.rtype == "MX"):
                reverse_record_delete(record.name, record.rdata.address)

            print record.toJSON()
            record.fromJSON(payload)
            print record.toJSON()
            zone.write_to_file(FILE_LOCATION[zone_origin])

            # create new reverse record
            if (record.rtype == "A" or record.rtype == "MX"):
                reverse_record_add(record.name, zone_origin, record.rdata.address, record.ttl)

            restart_bind(find_server(zone_origin))
            return HttpResponse('{"status" : "ok"}')
        except ValueError:
            return HttpResponse('{"status" : "Invalid JSON arguments"}')
        except KeyError as k_err:
            return HttpResponse('{"status" : "'+k_err.args[0]+'"}')
        except LookupError as l_err:
            return HttpResponse('{"status" : "'+l_err.args[0]+'"}')

    def post(self, request, zone_origin, record_name=""):
        """POST Method handler, used to create a new resource record.

        This endpoint recieve the following JSON file:
        {
            "name" : "new_record_name",
            "rclass" : "new_record_rclass",
            "ttl" : "new_record_ttl",
            "rtype" : "new_record_rtype",
            "rdata" : {
                "rdata_name1" : "data",
                ...
            },
        }
        Note that rclass and TTL are optional.

        This endpoint will return { "status" : "ok" } if adding a new record is
        successfull and {"status" : "fail"} otherwise
        """
        try:
            payload = json.loads(request.body.decode('utf-8'))

            if not (zone_origin in FILE_LOCATION):
                raise KeyError('Invalid Zone: ' + zone_origin)

            zone = DNSZone()
            zone.read_from_file(FILE_LOCATION[zone_origin])
            # print zone.toJSON()
            if (payload['rtype'] == "MX"):
                record_data = MXRecordData()
            elif (payload['rtype'] == "SOA"):
                record_data = SOARecordData()
            else:
                record_data = RecordData()
            new_record = DNSResourceRecord(rdata=record_data)
            new_record.fromJSON(payload)
            zone.add_record(new_record)
            print zone
            zone.write_to_file(FILE_LOCATION[zone_origin])

            # add reverse if rtype is A:
            if new_record.rtype == "A" or new_record.rtype == "MX":
                reverse_record_add(new_record.name, zone_origin,
                                   new_record.rdata.address, new_record.ttl)

            restart_bind(find_server(zone_origin))
            return HttpResponse('{"status" : "ok"}')
        except ValueError:
            return HttpResponse('{"status" : "Invalid JSON arguments"}')
        except KeyError as k_err:
            return HttpResponse('{"status" : "'+k_err.args[0]+'"}')
        except LookupError as l_err:
            return HttpResponse('{"status" : "'+l_err.args[0]+'"}')
