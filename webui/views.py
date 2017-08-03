# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse

from utils.zones_form import ZoneForm, RecordForm
from utils.message_notif import get_message_notif
from utils.api_service import *
from utils.active_port import check_active_port
from api.utils.config import FILE_LOCATION, ZONE_DICT, ZONE_SLAVES, LOG_DIR, REMOTE_MNT_DIR, LOCAL_MNT_DIR
from api.utils.parser import DNSZone
import json

# "DataState Dict"
def DataState(network_id, zones_id='', record_id=''):
    data_state = {}
    data_state['network_id'] = network_id
    data_state['zones_id'] = zones_id
    data_state['record_id'] = record_id
    return data_state

# "Dashboard View - Data Count & Active Port Checking"
def index(request):
    base_url_api = 'http://'+request.get_host()+"/api/"
    dashboard_count = {}
    dashboard_count['server_total'] = len(ZONE_DICT)
    dashboard_count['zones_total'] = len(FILE_LOCATION)
    dashboard_count['record_total'] = 0

    server_status = {}

    for record in FILE_LOCATION:
        result = json.loads(get_allrecord(base_url_api, record))
        dashboard_count['record_total'] = dashboard_count['record_total']+len(result['resource_records'])

    # "Check Active Port for each server."
    for server in ZONE_DICT:
            server_status[server] = check_active_port(server, 53)

    return render(request, 'index.html',{
                'dashboard_count' : dashboard_count,
                'server_status' : server_status,
            })

# "Networking View - Show list of Server"
def network(request):
    return render(request, 'network.html',{
                'network_dict' : ZONE_DICT,
            })

# "Help View"
def help(request):
    return render(request, 'help.html')

# "Zone View - List of Zones of a Server."
def zones(request, network_id):
    data_state = DataState(network_id)
    message_notif = ''
    zones_list = ZONE_DICT[network_id]
    slave_list = ZONE_SLAVES[network_id]

    for zone in slave_list:
        if zone != '':
            dnszone = DNSZone()
            dnszone.read_from_file(FILE_LOCATION[zone])
            soa_record = dnszone.find_record('@', None, 'SOA', None)
            soa_serial = int(soa_record.rdata.serial_no)
            print "SOA_SERIAL: " + str(soa_serial)
            for slave in slave_list[zone]:
                if slave != '':
                    log_filename = LOG_DIR[slave].replace(REMOTE_MNT_DIR, LOCAL_MNT_DIR[slave], 1)
                    serial = 0
                    with open(log_filename, "r") as f:
                        lines = f.read()
                        search_str = 'zone ' + zone + '/IN: sending notifies (serial '
                        serial = int(lines.rsplit(search_str,1)[1].split(')')[0])
                        print "SLAVE SERIAL: " + str(serial)
                    if serial == soa_serial:
                        slave_list[zone][slave] = 'up-to-date'
                    else:
                        slave_list[zone][slave] = 'outdated'

    print slave_list
    # Set Message Notification
    if  request.method == 'GET' and 'status' in request.GET:
        message_notif=get_message_notif(request.GET['status'])
    if  request.method == 'GET' and 'hostname' in request.GET:
        message_notif=get_message_notif(request.GET['status'], request.GET['hostname'])


    return render(request, 'zones.html',{
                'network_id' : network_id,
                'zones_list' : zones_list,
                'message_notif': message_notif,
                'slave_list': slave_list,
            })

# "Add New Zone View - Add Zone Form"
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

# "Zone Manage View - Add Record Form, List of Record View"
def zones_manage(request, network_id, zones_id):
    base_url_api = 'http://'+request.get_host()+"/api/"
    data_state = DataState(network_id,zones_id)
    records_data = {}
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

    # Get All Record from zones_id
    try :
        records_data = json.loads(get_allrecord(base_url_api,zones_id))
        printJSONObject(records_data)
    except BaseException as b_error :
        message_notif = get_message_notif('error','get_all_record: '+str(b_error))
    except :
        message_notif = get_message_notif('error','get_all_record errors')

    return render(request, 'zones-manage.html', {
                'network_id' : network_id,
                'zones_id': zones_id,
                'message_notif': message_notif,
                'records_data' : records_data,
            })

# "Record Manage View - Edit Form View"
def records_manage(request, network_id, zones_id, record_id):
    base_url_api = 'http://'+request.get_host()+"/api/"
    data_state = DataState(network_id,zones_id,record_id)
    record_data = {}
    record = {}
    message_notif = request.session.get('message_notif', None)
    request.session['message_notif'] = ''

    # Get Single Record Data
    try :
        record['name']=record_id
        record['type']=''
        record['address']=''
        if  request.method == 'GET' and 'type' in request.GET:
            record['type']=request.GET['type']
        if  request.method == 'GET' and 'address' in request.GET:
            record['address']=request.GET['address']

        record_data = json.loads(get_record(base_url_api,zones_id,record))
        printJSONObject(record_data)
    except BaseException as b_error :
        message_notif = get_message_notif('error','get_record: '+str(b_error))
    except :
        message_notif = get_message_notif('error','get_record errors')

    return render(request, 'records-manage.html', {
                'network_id' : network_id,
                'zones_id': zones_id,
                'record_id': record_id,
                'record_data': record_data,
                'message_notif': message_notif,
            })

# "Record Manage Action - Edit and Delete Action endpoint"
def records_action(request, network_id, zones_id, record_id, action):
    base_url_api = 'http://'+request.get_host()+"/api/"
    data_state = DataState(network_id,zones_id,record_id)
    message_notif = {}
    url_rvr = reverse('records_manage',args=[network_id,zones_id,record_id])

    if action == 'edit':
        form = RecordForm(request.POST)
        try :
            message_notif = apiServiceNotif('update_record',base_url_api,data_state,form)
            if message_notif['type_notif'] == 'success' :
                url_rvr = reverse('records_manage',args=[network_id,zones_id,message_notif['message_item']])
            else :
                url_rvr = reverse('records_manage',args=[network_id,zones_id,record_id])

            request.session['message_notif'] = message_notif
            if  request.method == 'POST' and 'type' in request.GET:
                redirect(url_rvr+'?type='+request.GET['type'])
            return redirect(url_rvr)
        except BaseException as b_error :
            message_notif = get_message_notif('error','records_action edit : '+str(b_error))
        except :
            message_notif = get_message_notif('error','records_action Edit Errors')


    elif action == 'delete':
        try :
            message_notif = apiServiceNotif('delete_record',base_url_api,data_state)
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

# "Debug View"
def debug(request):
    return HttpResponse('bla')
