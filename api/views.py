# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt

"""This method serve:
        GET to retrieve information about NS record
        POST to create a new record in a file
"""
@csrf_exempt
def file(request, arg):
    if request.method == "GET":
        return file_get(request, arg)
    elif request.method == "POST":
        return file_post(request, arg)
    else:
        raise Http404("This method doesn't exist")

def file_post(req, arg):
    return HttpResponse("Hello, file post." + str(arg))

def file_get(req, arg):
    return HttpResponse("Hello, file get." + str(arg))


"""This method serve:
        GET to retrieve information about NS record
        PUT to update a NS record
        DELETE to delete a NS record
"""
@csrf_exempt
def record(request, arg, arg2):
    if request.method == "GET":
        return record_get(request, arg, arg2)
    elif request.method == "PUT":
        return record_put(request, arg, arg2)
    elif request.method == "DELETE":
        return record_delete(request, arg, arg2)
    else:
        raise Http404("This method doesn't exist")

def record_get(req, arg, arg2):
    return HttpResponse("Hello, record get." + str(arg) + " " + str(arg2))

def record_put(req, arg, arg2):
    return HttpResponse("Hello, record put." + str(arg) + " " + str(arg2))

def record_delete(req, arg, arg2):
    return HttpResponse("Hello, record delete." + str(arg) + " " + str(arg2))
