#!/usr/bin/env python3

import json, csv, logging, os, sys, requests, datetime, threading
import logging.handlers
from requests.auth import HTTPBasicAuth

def send_logs_to_bds(json_file, csv_file, search_key='value', syslog_host='10.125.22.131', syslog_port=514):
    path = '/tmp'
    try:
        if sys.platform == "Windows":
            path = "C:\\Users\\temp"
            os.system("md " + path)    
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    else:
        os.chdir(path)
        f = open(json_file)
        data = json.load(f)
        f_data = data[search_key]
        f.close()
        temp_file = open(csv_file, 'w')
        csvwriter =  csv.writer(temp_file)
        count = 0
        for i in f_data:
            if count == 0:
                header = i.keys()
                csvwriter.writerow(header)
                count += 1
            csvwriter.writerow(i.values())
        temp_file.close()
        try:
            if os.path.exists(csv_file):
                my_logger = logging.getLogger('MyLogger')
                my_logger.setLevel(logging.INFO)
                handler = logging.handlers.SysLogHandler(address = (syslog_host,syslog_port))
                my_logger.addHandler(handler)
                file_reader = open(csv_file)
                read = csv.reader(file_reader)
                for row in read:
                   my_logger.info(row)
                temp_file.close()
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        return ''

def main(env,key):
    url = "https://login.microsoftonline.com/acf00694-f6ba-46e5-8b3a-bd2aa764bc58/oauth2/token"
    id = "336aead1-29c5-42eb-8b11-9676f68c844f"
    token = "FHR62WocL4nooRQIIyv5RM0/rV7dunYOGscotQx6vn4="

    params = {
        "grant_type":"client_credentials",
        "client_id": id,
        "client_secret": token,
         "resource": "https://management.azure.com/"
    }

    resp = requests.post(url, data=params, auth=HTTPBasicAuth(id, token))
    result = json.loads(resp.text)
    new_token = "Bearer " +(result['access_token'])
    start_time = datetime.datetime.utcnow()
    end_time = start_time - datetime.timedelta(minutes=25)
    stime = start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    etime = end_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    f = '$filter' + "=eventTimestamp ge '" + etime + "' and eventTimestamp le '" + stime + "'"
    s = "$select=correlationId,authorization,caller,description,eventDataId,eventName,category,eventTimestamp,id,level,operationId,operationName,resourceGroupName,resourceProviderName,resourceType,resourceId,status,subscriptionId,properties"

    headers = {
      'Content-type': 'application/json',
      'Authorization': new_token
    }
    get_logs_api = (("https://management.azure.com/subscriptions/%s/providers/microsoft.insights/eventtypes/management/values?api-version=2015-04-01&%s&%s") % (key,f,s))
    r = requests.get(get_logs_api, headers=headers)
    api_data = json.loads(r.text)
    file_path_default = "D:/AzureAccessLogging"
    log_file_name = env+".json"
    csv_file_name = env+".csv"
    with open(log_file_name, 'w') as file:
        json.dump(api_data, file)
    send_logs_to_bds(json_file=file_path_default+log_file_name, csv_file=file_path_default+csv_file_name)

    return 'Completed'

if __name__ == '__main__':
    keys = {'Prod': '0ad137c6-ecae-4bb2-bc5c-d9b5d6014b03', 'Lab': '05954432-22b1-44f0-8569-ca05cf50aed4', 'MGMT': '9accc546-a44f-409e-8b05-01d08b4d5c31', 'non-prod_Infra': '27d2ef08-be9c-4a60-902c-c8f1d97b6ce7', 'Test': '4a49d5da-fff5-4f07-a5d8-274f29c7d738', 'Dev': '3b5981b3-bad4-47da-bd8a-f8f4e2ea90b1', 'Innovation': 'a6fb7f44-ffd9-4fef-a7f1-d5e3cbc33bd6'}
    threads = []
    for x,y in keys.items():
        t = threading.Thread(target=main, args=(x,y))
        threads.append(t)
        t.start()
    #keys = {'test': '4a49d5da-fff5-4f07-a5d8-274f29c7d738'}
    threads = []
    for x,y in keys.items():
        t = threading.Thread(target=main, args=(x,y))
        threads.append(t)
        t.start()