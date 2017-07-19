# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse

from utils.zones_form import ZoneForm
from utils.message_notif import get_message_notif
from utils.api_service import *
from api.settings import ZONE_DICT
import json
import requests




def index(request):
    return render(request, 'index.html')

def network(request):
    return render(request, 'network.html',{
                'network_dict' : ZONE_DICT,
            })

def zones(request, network_id):
    zones_list = ZONE_DICT[network_id];
    return render(request, 'zones.html',{
                'network_id' : network_id,
                'zones_list' : zones_list,
            })

def zones_manage(request, network_id, zones_id):

    base_url_api = 'http://'+request.get_host()+"/api/"
    url_rvr = reverse('zones_manage',args=[network_id,zones_id])
    message_notif = ''

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        form = ZoneForm(request.POST)
        if form.is_valid():
            f_hostname = form.cleaned_data['f_hostname']
            result = json.loads(post_record(base_url_api,form,zones_id,f_hostname))

            if result["status"] == 'ok' :
                return redirect(url_rvr+'?status=success_add&hostname='+f_hostname)
            else :
                return redirect(url_rvr+'?status=failed_add')
        else:
            return redirect(url_rvr+'?status=failed_add')

    # Set Message Notification
    if  request.method == 'GET' and 'status' in request.GET:
        message_notif=get_message_notif(request.GET['status'])
    if  request.method == 'GET' and 'hostname' in request.GET:
        message_notif=get_message_notif(request.GET['status'], request.GET['hostname'])

    return render(request, 'zones-manage.html', {
                'network_id' : network_id,
                'zones_id': zones_id,
                'message_notif': message_notif,
            })

def records_manage(request, network_id, zones_id, record_id):
    base_url_api = 'http://'+request.get_host()+"/api/"
    message_notif = ''

    record_data = json.loads(get_record(base_url_api,zones_id,record_id))
    printJSONObject(record_data)

    # Set Message Notification
    if  request.method == 'GET' and 'status' in request.GET:
        message_notif=get_message_notif(request.GET['status'])
    if  request.method == 'GET' and 'hostname' in request.GET:
        message_notif=get_message_notif(request.GET['status'], request.GET['hostname'])

    return render(request, 'records-manage.html', {
                'network_id' : network_id,
                'zones_id': zones_id,
                'record_id': record_id,
                'record_data': record_data,
                'message_notif': message_notif,
            })


def records_action(request, network_id, zones_id, record_id, action):
    base_url_api = 'http://'+request.get_host()+"/api/"
    url_rvr = reverse('records_manage',args=[network_id,zones_id,record_id])
    print 'Action : '+action

    if action == 'edit':
        form = ZoneForm(request.POST)
        if form.is_valid():
            f_hostname = form.cleaned_data['f_hostname']
            result = json.loads(update_record(base_url_api,form,zones_id,record_id,f_hostname))
            url_rvr = reverse('records_manage',args=[network_id,zones_id,f_hostname])

            if result["status"] == 'ok' :
                return redirect(url_rvr+'?status=success_edit&hostname='+f_hostname)
            else :
                return redirect(url_rvr+'?status=failed_edit')
        else:
            return redirect(url_rvr+'?status=failed_edit')

    if action == 'delete':
        result = json.loads(delete_record(base_url_api, zones_id, record_id))
        url_rvr = reverse('zones_manage',args=[network_id,zones_id])
        if result["status"] == 'ok' :
            return redirect(url_rvr+'?status=success_del&hostname='+record_id)
        else :
            return redirect(url_rvr+'?status=failed_del')


    return HttpResponse('action')


def debug(request):
    return HttpResponse('bla')
