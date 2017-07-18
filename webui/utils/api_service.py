import requests
import json
import ast


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
