from message_notif import get_message_notif
from api.utils.config import FILE_LOCATION,ZONE_DICT
import requests
import json
import ast


def get_allrecord(base_url_api, zone_id):
    response = requests.get(base_url_api+'zone/'+zone_id)
    return response.content

def get_record(base_url_api, zone_id, record):
    get_data = {
      "rtype" : record['type']
    }
    response = requests.get(base_url_api+'record/'+zone_id+'/'+record['name'], data=json.dumps(get_data))
    return response.content

def post_record(base_url_api,form_record,zones_id,f_hostname):
    f_value = form_record.cleaned_data['f_value']
    f_ttl = form_record.cleaned_data['f_ttl']
    f_type = form_record.data['f_type']
    f_priority = form_record.cleaned_data['f_priority']
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
    response = requests.post(base_url_api+'record/'+zones_id+'/', data=json.dumps(post_data), headers=headers)

    return response.content


def update_record(base_url_api,form_record,zones_id,record,f_hostname):
    f_value = form_record.cleaned_data['f_value']
    f_ttl = form_record.cleaned_data['f_ttl']
    f_type = form_record.data['f_type']
    f_priority = form_record.cleaned_data['f_priority']
    # redirect to a new URL:
    put_data = {
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
    response = requests.put(base_url_api+'record/'+zones_id+'/'+record, data=json.dumps(put_data), headers=headers)

    return response.content

def delete_record(base_url_api, zone_id, record_id):
    response = requests.delete(base_url_api+'record/'+zone_id+'/'+record_id)
    return response.content

def post_zones(base_url_api,network_id,form_zone,f_zonename):

    f_zonename = form_zone.cleaned_data['f_zonename']
    f_zoneclass = form_zone.cleaned_data['f_zoneclass']
    zone_name = "zone " + '"' + f_zonename + '" ' + f_zoneclass
    post_data = {
        "zone": {
            zone_name: {}
        }
    }

    zonetype = form_zone.cleaned_data['f_zonetype']
    post_data['zone'][zone_name]['type'] = zonetype

    if (zonetype == "master"):
        post_data['soa_record'] = {}
        post_data['soa_record']['authoritative_server'] = form_zone.cleaned_data['f_authserv']
        post_data['soa_record']['admin_email'] = form_zone.cleaned_data['f_adminemail']
        post_data['soa_record']['serial_no'] = form_zone.cleaned_data['f_serialno']
        post_data['soa_record']['slv_refresh_period'] = form_zone.cleaned_data['f_slvrefresh']
        post_data['soa_record']['slv_retry'] = form_zone.cleaned_data['f_slvretry']
        post_data['soa_record']['slv_expire'] = form_zone.cleaned_data['f_slvexpire']
        post_data['soa_record']['max_time_cache'] = form_zone.cleaned_data['f_maxtimecache']
        post_data['zone'][zone_name]['file'] = '"' + form_zone.cleaned_data['f_zonefilename'] + '"'
        post_data['directives'] = {}
        f_directive = (form_zone.cleaned_data['f_directive']).split(';')
        for d in f_directive:
            if (d != ''):
                d_key = d.split(' ')[0]
                d_value = d.split(' ')[1]
                post_data['directives'][d_key] = d_value
    elif (zonetype == "forward"):
        post_data['zone'][zone_name]['forwarders'] = '{' + form_zone.cleaned_data['f_forwarders'] + '}'
    elif (zonetype == "slave"):
        post_data['zone'][zone_name]['masters'] = form_zone.cleaned_data['f_masters']
        post_data['zone'][zone_name]['file'] = '"' + form_zone.cleaned_data['f_zonefilename'] + '"'

    #Add statements to zone
    f_statement = form_zone.cleaned_data['f_statement'].split('#')
    for statement in f_statement:
        statement = str(statement)
        if statement != '':
            key = statement.split(':')[0]
            val = '{ ' + statement.split(':')[1] + ' }'
            if key != '':
                post_data['zone'][zone_name][key] = val
    # redirect to a new URL:
    headers = {'content-type': 'application/json'}
    response = requests.post(base_url_api+'zone/'+network_id, data=json.dumps(post_data), headers=headers)

    return response.content

def printJSONObject(data, indent=0):
    if isinstance(data, list):
        print
        for item in data:
            printJSONObject(item, indent+1)
    elif isinstance(data, dict):
        print
        for k, v in data.iteritems():
            print "    " * indent, k + ":",
            printJSONObject(v, indent + 1)
    else:
        print data


###### MASTER apiService ######
def apiServiceNotif(call_type, base_url_api, data_state, form_data=None) :
    f_hostname = ''
    message_notif = {}
    result = {}

    try :
        # GET Record
        if call_type == 'get_record' :
            print "Call GET Record"
        # GET ALL Record
        elif call_type == 'getall_record' :
            print "Call GET ALL Record"

        # POST New Record
        elif call_type == 'post_record' :
            if form_data.is_valid():
                f_hostname = form_data.cleaned_data['f_hostname']
                result = json.loads(post_record(base_url_api,form_data,data_state['zones_id'],f_hostname))
                if result["status"] == 'ok' :
                    message_notif = get_message_notif('success_add',f_hostname)
                else :
                    message_notif = get_message_notif('failed_add',f_hostname+' - '+result["status"])
            else:
                message_notif = get_message_notif('failed_add',"Form Data Invalid")

        # UPDATE Record
        elif call_type == 'update_record' :
            if form_data.is_valid():
                f_hostname = form_data.cleaned_data['f_hostname']
                result = json.loads(update_record(base_url_api,form_data,data_state['zones_id'],data_state['record_id'],f_hostname))
                if result["status"] == 'ok' :
                    message_notif = get_message_notif('success_edit',f_hostname)
                else :
                    message_notif = get_message_notif('failed_edit',f_hostname+' - '+result["status"])
            else:
                message_notif = get_message_notif('failed_edit',"Form Data Invalid")

        # DELETE Record
        elif call_type == 'delete_record' :
            result = json.loads(delete_record(base_url_api, data_state['zones_id'], data_state['record_id']))
            if result["status"] == 'ok' :
                message_notif = get_message_notif('success_delete',data_state['record_id'])
            else :
                message_notif = get_message_notif('failed_delete',data_state['record_id']+' - '+result["status"])

        # POST New Zone
        elif call_type == 'post_zones' :
            if form_data.is_valid():
                f_hostname = form_data.cleaned_data['f_zonename']
                network_id = data_state['network_id']
                result = json.loads(post_zones(base_url_api,network_id,form_data,f_hostname))

                if result["status"] == 'ok' :
                    message_notif = get_message_notif('success_addzone',f_hostname)
                else :
                    message_notif = get_message_notif('failed_addzone',f_hostname+' - '+result["status"])

        else  :
            message_notif = get_message_notif('error','API Service : Undefined API call_type')

    except BaseException as b_error :
        message_notif = get_message_notif('error','API Service : '+str(b_error.args[0]))
    except :
        message_notif = get_message_notif('error','API Service : Unexpected Errors')

    return message_notif;
