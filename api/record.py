"""Class-based view for record handling."""
import json
from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from dns import DNSZone
from settings import FILE_LOCATION

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

        And return {"status" : "notfound"} if the record or zone file is not exist
        """
        try:
            payload = json.loads(request.body.decode('utf-8'))
            rclass = payload.get("rclass")
            rtype = payload.get("rtype")
            rdata = payload.get("rdata")

            zone = DNSZone()
            zone.read_from_file(FILE_LOCATION[zone_origin])
            record = zone.find_record(record_name, rclass, rtype, rdata)
            return HttpResponse(record.toJSON() if record
                                else "{'status' : 'notfound'}")
        except:
            return HttpResponse("{'status' : 'notfound'}")

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
            payload = json.loads(request.body.decode('utf-8'))
            rclass = payload.get("rclass")
            rtype = payload.get("rtype")
            rdata = payload.get("rdata")

            zone = DNSZone()
            zone.read_from_file(FILE_LOCATION[zone_origin])
            zone.delete_record(record_name, rclass, rtype, rdata)
            print zone
            zone.write_to_file(FILE_LOCATION[zone_origin])
            return HttpResponse("{'status' : 'ok'}")
        except:
            return HttpResponse("{'status' : 'failed'}")

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
            # print body
            zone = DNSZone()

            zone.read_from_file(FILE_LOCATION[zone_origin])
            record = zone.find_record(record_name)
            print record.toJSON()
            record.fromJSON(payload)
            print record.toJSON()
            # zone.write_to_file(FILE_LOCATION[zone_origin])
            return HttpResponse("{'status' : 'ok'}")
        except:
            return HttpResponse("{'status' : 'failed'}")

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
