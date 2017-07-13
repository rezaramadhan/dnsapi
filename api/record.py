"""Class-based view for record handling."""
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

    http_method_names = ['get', 'put', 'delete']

    def get(self, request, zone_origin, record_name):
        """GET Method handler, used to retrieve all information about a record.

        This endpoint recieve no JSON data. If there's any, it will be ignored.

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
        """
        try:
            zone = DNSZone()
            zone.read_from_file(FILE_LOCATION[zone_origin])
            print zone.find_record(record_name).toJSON()
            # handle the get request
            return HttpResponse("{'status': 'ok'}")
        except:

    def delete(self, request, zone_origin, record_name):
        """DELET Method handler, used to delete a record.

        This endpoint recieve no JSON data. If there's any, it will be ignored.

        This endpoint will return { "status" : "ok" } if deleting a record is
        successfull and {"status" : "fail"} otherwise
        """
        # handle the post request
        return HttpResponse("Hello, record delete." + str(zone_origin))

    def put(self, request, zone_origin, record_name):
        """GET Method handler, used to update a record.

        This endpoint recieve the following JSON file:
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
        Note that all field is optional. You only need to use it if you want to
        update the value.

        This endpoint will return { "status" : "ok" } if updating a record is
        successfull and {"status" : "fail"} otherwise
        """
        # handle the get request
        return HttpResponse("Hello, record put." + str(zone_origin))
