# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse

from utils.zones_form import ZoneForm
from utils.message_notif import get_message_notif
import json
import requests


def index(request):
    return render(request, 'index.html')

def network(request):
    return render(request, 'network.html')

def zones(request, zones_id):
    url_api = 'http://127.0.0.1:8080/api/'+zones_id
    message_notif = ''
    # if this is a POST request we need to process the form data
    # return HttpResponse(request.method)

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ZoneForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            f_hostname = form.cleaned_data['f_hostname']
            f_value = form.cleaned_data['f_value']
            f_ttl = form.cleaned_data['f_ttl']
            f_type = form.data['f_type']
            f_priority = form.cleaned_data['f_priority']
            # redirect to a new URL:
            post_data = {
              "name": f_hostname,
              "rclass": "IN",
              "rdata": {
                "address": f_value,
                "priority": f_priority
              },
              "rtype": f_type,
              "ttl": f_ttl
            }

            headers = {'content-type': 'application/json'}
            response = requests.post(url_api, data=json.dumps(post_data),  headers=headers)
            content = response.content

            url_rvr = reverse('zones',args=[zones_id])
            return redirect(url_rvr+'?status=success_add&hostname='+f_hostname)
        else:
            return redirect(url_rvr+'?status=failed_add')

    if  request.method == 'GET' and 'status' in request.GET:
        message_notif=get_message_notif(request.GET['status'])
    if  request.method == 'GET' and 'hostname' in request.GET:
        message_notif=get_message_notif(request.GET['status'], request.GET['hostname'])

    return render(request, 'zones-manage.html', {
                'zones_id': zones_id,
                'message_notif': message_notif,
            })

def debug(request):
    return HttpResponse('bla')
