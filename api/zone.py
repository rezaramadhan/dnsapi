from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from settings import FILE_LOCATION
from dns import *

@method_decorator(csrf_exempt, name='dispatch')
class ZoneView(View):
    """ZoneView, a generic view class-based-view.

    This view handles:
        GET to retrieve all NS record within a file
        POST to create a new record in a file
    """

    http_method_names = ['get', 'post']

    def post(self, request, zone_origin):
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
            body = json.loads(request.body.decode('utf-8'))
            zone = DNSZone()
            zone.read_from_file(FILE_LOCATION[zone_origin])
            # print zone.toJSON()
            new_record = DNSResourceRecord()
            new_record.fromJSON(body)
            zone.add_record(new_record)
            print new_record.toJSON()
            zone.write_to_file(FILE_LOCATION[zone_origin])
            return HttpResponse("{ 'status' : 'ok' }")
        except:
            return HttpResponse("{ 'status' : 'fail' }")

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
