import requests
import json
import ast


def get_allrecord(base_url_api, zone_id):
    response = requests.get(base_url_api+'zone/'+zone_id)
    return response.content

def get_record(base_url_api, zone_id, record):
    response = requests.get(base_url_api+'record/'+zone_id+'/'+record)
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
    print base_url_api+'record/'+zones_id+'/'+record+'/'
    response = requests.put(base_url_api+'record/'+zones_id+'/'+record, data=json.dumps(put_data), headers=headers)
    print "EDIT DATA :"
    print response.content
    return response.content

def delete_record(base_url_api, zone_id, record):
    response = requests.delete(base_url_api+'record/'+zone_id+'/'+record)
    return response.content

def post_zones(base_url_api,named_conf,form_zone,f_zonename):

    f_directive = form_zone.cleaned_data['f_directive']
    f_authserv = form_zone.cleaned_data['f_authserv']
    f_serialno = form_zone.cleaned_data['f_serialno']
    f_slvrefresh = form_zone.cleaned_data['f_slvrefresh']
    f_slvretry = form_zone.cleaned_data['f_slvretry']
    f_slvexpire = form_zone.cleaned_data['f_slvexpire']
    f_maxtimecache = form_zone.cleaned_data['f_maxtimecache']
    f_adminemail = form_zone.cleaned_data['f_adminemail']
    f_zonetype = form_zone.cleaned_data['f_zonetype']
    # redirect to a new URL:
    post_data = {
        "directives": {
            "directive1": f_directive
        },
        "soa_record": {
            "authoritative_server": f_authserv,
            "admin_email": f_adminemail,
            "serial_no": f_serialno,
            "slv_refresh_period": f_slvrefresh,
            "slv_retry": f_slvretry,
            "slv_expire": f_slvexpire,
            "max_time_cache": f_maxtimecache
        },
        "zone": {
            "zone ZONENAME": {
                "file": f_zonename,
                "type": f_zonetype
            }
        }
    }

    headers = {'content-type': 'application/json'}
    response = requests.post(base_url_api+'zone/'+named_conf+'/', data=json.dumps(post_data), headers=headers)

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
