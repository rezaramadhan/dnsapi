"""Class-based view for zone handling."""
from django.views.generic import View
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from settings import (FILE_LOCATION, LOCAL_MNT_DIR, DEFAULT_CONF_FILENAME,
                      REMOTE_MNT_DIR, restart_bind, init_data)
from dns import (DNSZone, DNSResourceRecord, RecordData, SOARecordData)
import iscpy
import json
import re
import logging
import traceback

logger = logging.getLogger(__name__)


def add_absolute_path(zone_body):
    """Add the absolute path to zone file path if necessary."""
    filename = zone_body[zone_body.keys()[0]]['file']
    filename = re.search('"(.*)"', filename).group(1)
    if filename[0] != '/':  # relative path
        filename = REMOTE_MNT_DIR + filename
    elif not (REMOTE_MNT_DIR in filename):
        raise EnvironmentError("Cannot access the provided path")
    zone_body[zone_body.keys()[0]]['file'] = '"' + filename + '"'
    logger.debug("Final zone_body: " + str(zone_body))


@method_decorator(csrf_exempt, name='dispatch')
class ZoneView(View):
    """ZoneView, a generic view class-based-view.

    This view handles:
        GET to retrieve all NS record within a file
        POST to create a new record in a file
    """

    http_method_names = ['get', 'post']

    def get(self, request, zone_origin):
        """GET Method handler, used to retrieve all information about a zone.

        This endpoint recieve no JSON data, if there's any, it will be ignored.

        This endpoint will return the following JSON file:
        {
            "origin" : "zone_origin",
            "directives" : {
                "directive1": "value1",
                ...
            }
            "records" : [
                {
                    "name" : "record_name",
                    "rclass" : "record_rclass",
                    "ttl" : "record_ttl",
                    "rtype" : "record_rtype",
                    "rdata" : {
                        "rdata_name1" : "data",
                        ...
                    },
                },
                ...
            ]
        }
        """
        # handle the get request
        try:
            if not (zone_origin in FILE_LOCATION):
                raise KeyError('Invalid Zone: ' + zone_origin)

            zone = DNSZone()
            zone.read_from_file(FILE_LOCATION[zone_origin])
            return HttpResponse(zone.toJSON())
        except ValueError as v_err:
            logger.warning(v_err.args)
            logger.warning(traceback.format_exc(2) + "\n\n\n")
            return HttpResponse('{"status" : "Invalid JSON arguments"}')
        except (KeyError, LookupError) as k_err:
            logger.error(k_err.args)
            logger.error(traceback.format_exc() + "\n\n\n")
            return HttpResponse('{"status" : "'+str(k_err.args[0])+'"}')
        except Exception as b_err:
            logger.error(b_err.args)
            logger.error(traceback.format_exc() + "\n\n\n")
            return HttpResponse('{"status" : "'+str(b_err)+'"}')

    def post(self, request, dns_server):
        """POST Method handler, used to create a new zone record.

        This endpoint recieve the following JSON file:
        {
            "directives": {
                "directive1": "value1",
                ...
            }
            "soa_record": {
                "authoritative_server": "",
                "admin_email": "",
                "serial_no": "",
                "slv_refresh_period": "",
                "slv_retry": "",
                "slv_expire": "",
                "max_time_cache": ""
            }
            "zone": {
                "zone ZONENAME": {
                    "file": "ZONE_FILE_PATH",
                    "type": "TYPE"
                    ...
                }
            }
        }
        Note that rclass and TTL are optional.

        This endpoint will return { "status" : "ok" } if adding a new record is
        successfull and {"status" : "fail"} otherwise
        """
        try:
            # Load input parameters
            body = json.loads(request.body.decode('utf-8'))
            body_directives = body['directives']
            body_soa = body['soa_record']
            body_zone = body['zone']
            add_absolute_path(body_zone)

            named_file = str(LOCAL_MNT_DIR[dns_server]) + DEFAULT_CONF_FILENAME

            # Add zone to named config file
            named_dict, named_keys = iscpy.ParseISCString(open(named_file).read())
            new_dict = iscpy.AddZone(body_zone, named_dict)
            iscpy.WriteToFile(new_dict, named_keys, named_file)

            # Make new zone file
            zone = str(body_zone.keys()[0])
            soa = SOARecordData()
            soa.fromJSON(body_soa)
            soa_record = DNSResourceRecord("@", "", "", "SOA", soa)
            resourcerecord = []
            resourcerecord.append(soa_record)
            ns_record = DNSResourceRecord("@", "", "", "NS",
                                          RecordData(body_soa['authoritative_server']))
            resourcerecord.append(ns_record)
            new_zone = DNSZone(body_directives, resourcerecord)
            zone_file = body_zone[zone]['file'].split('"')[1]
            zone_file = zone_file.replace(REMOTE_MNT_DIR,
                                          LOCAL_MNT_DIR[dns_server])

            print new_zone.toJSON()
            new_zone.write_to_file(zone_file)

            restart_bind(dns_server)

            init_data()
            return HttpResponse('{ "status" : "ok" }')
        except ValueError as v_err:
            logger.warning(v_err.args)
            logger.warning(traceback.format_exc(2) + "\n\n\n")
            return HttpResponse('{"status" : "Invalid JSON arguments"}')
        except (KeyError, LookupError) as k_err:
            logger.error(k_err.args)
            logger.error(traceback.format_exc() + "\n\n\n")
            return HttpResponse('{"status" : "'+str(k_err.args[0])+'"}')
        except Exception as b_err:
            logger.error(b_err.args)
            logger.error(traceback.format_exc() + "\n\n\n")
            return HttpResponse('{"status" : "'+str(b_err)+'"}')
