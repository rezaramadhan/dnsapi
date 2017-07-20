# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse

from utils.zones_form import ZoneForm,RecordForm
from utils.message_notif import get_message_notif
from utils.api_service import *
from api.settings import FILE_LOCATION,ZONE_DICT,DEFAULT_CONF_FILENAME
import json
import requests


def DataState(network_id, zones_id='', record_id=''):
    data_state = {}
    data_state['network_id'] = network_id
    data_state['zones_id'] = zones_id
    data_state['record_id'] = record_id
    return data_state

def index(request):
    base_url_api = 'http://'+request.get_host()+"/api/"

    record_total = 0
    server_total = len(ZONE_DICT)
    zones_total = len(FILE_LOCATION)

    for record in FILE_LOCATION:
        result = json.loads(get_allrecord(base_url_api, record))
        record_total = record_total+len(result['resource_records'])

    return render(request, 'index.html',{
                'server_total' : server_total,
                'zones_total' : zones_total,
                'record_total' : record_total,
            })

def network(request):
    return render(request, 'network.html',{
                'network_dict' : ZONE_DICT,
            })

def zones(request, network_id):
    data_state = DataState(network_id)
    message_notif = ''
    zones_list = ZONE_DICT[network_id]

    # Set Message Notification
    if  request.method == 'GET' and 'status' in request.GET:
        message_notif=get_message_notif(request.GET['status'])
    if  request.method == 'GET' and 'hostname' in request.GET:
        message_notif=get_message_notif(request.GET['status'], request.GET['hostname'])


    return render(request, 'zones.html',{
                'network_id' : network_id,
                'zones_list' : zones_list,
                'message_notif': message_notif,
            })

def zones_add(request, network_id):
    base_url_api = 'http://'+request.get_host()+"/api/"
    data_state = DataState(network_id)
    message_notif = ''

    if request.method == 'POST':
        form = ZoneForm(request.POST)
        try :
            message_notif = apiServiceNotif('post_zones',base_url_api,data_state,form)
        except BaseException as b_error :
            message_notif = get_message_notif('error','zoned_add : '+str(b_error.args[0]))
        except :
            message_notif = get_message_notif('error','Zones Add Errors')

    return render(request, 'zones-add.html',{
                'network_id' : network_id,
                'message_notif': message_notif,
            })

def zones_manage(request, network_id, zones_id):
    base_url_api = 'http://'+request.get_host()+"/api/"
    data_state = DataState(network_id,zones_id)
    message_notif = {}
    message_notif = request.session.get('message_notif', None)
    request.session['message_notif'] = ''


    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        form = RecordForm(request.POST)
        try :
            message_notif = apiServiceNotif('post_record',base_url_api,data_state,form)
        except BaseException as b_error :
            message_notif = get_message_notif('error',str(b_error))
        except :
            message_notif = get_message_notif('error','Zones Manage Errors')

    return render(request, 'zones-manage.html', {
                'network_id' : network_id,
                'zones_id': zones_id,
                'message_notif': message_notif,
            })


def records_manage(request, network_id, zones_id, record_id):
    base_url_api = 'http://'+request.get_host()+"/api/"
    data_state = DataState(network_id,zones_id,record_id)
    message_notif = request.session.get('message_notif', None)
    request.session['message_notif'] = ''

    record_data = json.loads(get_record(base_url_api,zones_id,record_id))
    printJSONObject(record_data)

    return render(request, 'records-manage.html', {
                'network_id' : network_id,
                'zones_id': zones_id,
                'record_id': record_id,
                'record_data': record_data,
                'message_notif': message_notif,
            })


def records_action(request, network_id, zones_id, record_id, action):
    base_url_api = 'http://'+request.get_host()+"/api/"
    data_state = DataState(network_id,zones_id,record_id)
    message_notif = {}
    url_rvr = reverse('records_manage',args=[network_id,zones_id,record_id])
    print 'Action : '+action

    if action == 'edit':
        form = RecordForm(request.POST)
        try :
            message_notif = apiServiceNotif('update_record',base_url_api,data_state,form)
        except BaseException as b_error :
            message_notif = get_message_notif('error','records_action edit : '+str(b_error))
        except :
            message_notif = get_message_notif('error','records_action Edit Errors')

    elif action == 'delete':
        try :
            message_notif = apiServiceNotif('delete_record',base_url_api,data_state,form)
        except BaseException as b_error :
            message_notif = get_message_notif('error','records_action delete : '+str(b_error))
        except :
            message_notif = get_message_notif('error','records_action Edit Errors')

        url_rvr = reverse('zones_manage',args=[network_id,zones_id])
        request.session['message_notif'] = message_notif
        return redirect(url_rvr)


    else :
        message_notif = get_message_notif('error','action undefined')

    request.session['message_notif'] = message_notif
    return redirect(url_rvr)


def debug(request):
    return HttpResponse('bla')
