from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse, Http404

class FileView(View):
    def post(self, request, arg):
        # handle the post request
        return HttpResponse("Hello, file post." + str(arg))

    def get(self, request, arg):
        # handle the get request
        return HttpResponse("Hello, file get." + str(arg))
