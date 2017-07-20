#dnsapi

##Description
dnsapi provides API to retrieve and modify BIND files. Return formats of all endpoints is in JSON.

##Requirements
* iscpy python library

##Endpoints

###Zone
* `GET` zone/zone_origin
  * Description

    Retrieve information for specified zone file.

  * Parameters

    __zone_origin__ (_required_) - The zone domain name

  * Return formats

    A JSON object of directives and records contained in the zone file with the following format:
    ```
    {
        "origin" : "zone_origin",
        "directives" : {
            "directive1": "value1",
            ...
        }
        "records" : [
            {
                "name" : "record_name",
                "rclass" : "record_rclass",
                "ttl" : "record_ttl",
                "rtype" : "record_rtype",
                "rdata" : {
                    "rdata_name1" : "data",
                    ...
                },
            },
            ...
        ]
    }
    ```

  * Errors

    Will return `status` key with error description.

* `POST` zone/named_file
  * Description

    Add a zone to named configuration file. Also creates the corresponding zone file with SOA record inside. This endpoint receives zone definition in JSON format.

  * Parameters

    __named_file__ (_required_) - The named configuration file name

  * Body

    ```
    {
        "directives": {
            "directive1": "value1",
            ...
        }
        "soa_record": {
            "authoritative_server": "",
            "admin_email": "",
            "serial_no": "",
            "slv_refresh_period": "",
            "slv_retry": "",
            "slv_expire": "",
            "max_time_cache": ""
        }
        "zone": {
            "zone ZONENAME": {
                "file": "ZONE_FILE_PATH",
                "type": "TYPE"
                ...
            }
        }
    }
    ```

  * Return format

    Will return `status` key with value `OK` if succeed, or `Invalid JSON arguments` if failed.

###Record
* `GET` record/zone_origin/record_name
  * Description

    Retrieve record details.

  * Parameters

    __zone_origin__ (_required_) - The zone domain name <br>
    __record_name__ (_required_) - The record name in the zone file

  * Body

    Receive the following JSON object (_optional_)
    ```
    {
        "rclass" : "record_rclass",
        "rtype" : "record_rtype",
        "rdata" : {
            "rdata_name1" : "data",
            ...
        },
    }
    ```
  * Return format

    A JSON object containing information of specified record with the following format:
    ```
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
    ```

  * Errors

    Returns `Invalid Zone` if zone_origin is not found in named config file. <br>
    Returns `status` key with value `notfound` if the record name is not found. <br>
    Returns `status` key with value `Invalid JSON arguments` if the information in optional search arguments is not valid
    Returns `status` key with other error description for _KeyError_ or _LookupError_

* `POST` record/zone_origin/record_name
  * Description

    Add a record to a specified zone file.

  * Parameters

    __zone_origin__ (_required_) - The zone domain name <br>
    __record_name=""__ (_default_) - The record name in the zone file
  * Body
    ```
    {
        "name" : "new_record_name",
        "rclass" : "new_record_rclass",
        "ttl" : "new_record_ttl",
        "rtype" : "new_record_rtype",
        "rdata" : {
            "rdata_name1" : "data",
            ...
        },
    }
    ```
  * Return format

    Returns `status` key with `value` OK if succeed
  * Errors

    Returns `Invalid Zone` if zone_origin is not found in named config file. <br>
    Returns `status` key with value `invalid JSON arguments` if the input arguments not valid.<br>
    Returns `status` key with value error description if _KeyError_ or _LookupError_ is raised.

* `PUT` record/zone_origin/record_name
  * Description

    Updates information of a record in zone file.

  * Parameters

    __zone_origin__ (_required_) - The zone domain name <br>
    __record_name__ (_required_) - The record name in the zone file

  * Return format

    Returns `status` key with `value` OK if succeed

  * Errors

    Returns `Invalid Zone` if zone_origin is not found in named config file. <br>
    Returns `status` key with value `invalid JSON arguments` if the input arguments not valid.<br>
    Returns `status` key with value error description if _KeyError_ or _LookupError_ is raised.

* `DELETE` record/zone_origin/record_name
  * Description

    Delete `record_name` from corresponding zone file.

  * Parameters

    __zone_origin__ (_required_) - The zone domain name <br>
    __record_name__ (_required_) - The record name in the zone file

  * Return format

    Returns `status` key with `value` OK if succeed
  * Errors

    Returns `Invalid Zone` if zone_origin is not found in named config file. <br>
    Returns `status` key with value `invalid JSON arguments` if the input arguments not valid.<br>
    Returns `status` key with value error description if _KeyError_ or _LookupError_ is raised.
