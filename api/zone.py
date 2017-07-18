from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from settings import FILE_LOCATION
from dns import *
import iscpy

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
            zone = DNSZone()
            zone.read_from_file(FILE_LOCATION[zone_origin])
            return HttpResponse(zone.toJSON())
        # handle the get request
        except:
            return HttpResponse("{ 'status' : 'fail' }")

    def post(self, request, named_file):
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

            #Add zone to named config file
            named_dict, named_keys = iscpy.ParseISCString(open(FILE_LOCATION[named_file]).read())
            new_dict = iscpy.AddZone(body_zone, named_dict)
            iscpy.WriteToFile(new_dict, named_keys, FILE_LOCATION[named_file])

            #Make new zone file
            zone = str(body_zone.keys()[0])
            soa = SOARecordData()
            soa.fromJSON(body_soa)
            new_record = DNSResourceRecord("", "", "@", "SOA", soa)
            resourcerecord = []
            resourcerecord.append(new_record)
            new_zone = DNSZone(body_directives, resourcerecord)
            new_zone.write_to_file(body_zone[zone]['file'].split('"')[1])
            return HttpResponse("{ 'status' : 'ok' }")
        except:
            return HttpResponse("{ 'status' : 'fail' }")
