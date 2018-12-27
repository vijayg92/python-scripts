#!/usr/bin/env python3
import json, csv, logging, os, sys, requests, datetime, threading, logging.handlers
from requests.auth import HTTPBasicAuth

def convert_json_csv(json_file_path, csv_file_path, search_key='value'):

    try:
        if os.path.exists(json_file_path):
            f = open(json_file_path)
            data = json.load(f)
            f_data = data[search_key]
            f.close()
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    else:
        temp_file = open(csv_file_path, 'w')
        csvwriter = csv.writer(temp_file)
        count = 0
        for i in f_data:
            if count == 0:
                header = i.keys()
                csvwriter.writerow(header)
                count += 1
            csvwriter.writerow(i.values())
        temp_file.close()
    return temp_file

def send_logs_to_bds(csf_file_to_send,syslog_host='10.125.22.131',syslog_port=514):
        my_logger = logging.getLogger('MyLogger')
        my_logger.setLevel(logging.INFO)
        handler = logging.handlers.SysLogHandler(address=(syslog_host,syslog_port))
        my_logger.addHandler(handler)
        try:
            if os.path.exists(csv_file_to_send):
                file_reader= open(csv_file_to_send)
                read = csv.reader(file_reader)
            for row in read:
                my_logger.info(row)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        return ''

def main(env,key):

    url = "https://login.microsoftonline.com/xxxxxxxxxxx/oauth2/token"
    id = "xxxxxxxxxxxxxxx"
    token = "xxxxxxxxxxxxx"

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
    end_time = start_time - datetime.timedelta(minutes=15)
    stime = start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    etime = end_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    f = '$filter' + "=eventTimestamp ge '" + etime + "' and eventTimestamp le '" + stime + "'"
    s = "$select=correlationId,authorization,caller,description,eventDataId,eventName,category,eventTimestamp,id,level,operationId,operationName,resourceGroupName,resourceProviderName,resourceType,resourceId,status,subStatus,subscriptionId,properties"

    headers = {
      'Content-type': 'application/json',
      'Authorization': new_token
    }
    get_logs_api = (("https://management.azure.com/subscriptions/%s/providers/microsoft.insights/eventtypes/management/values?api-version=2015-04-01&%s&%s") % (key,f,s))
    r = requests.get(get_logs_api, headers=headers)

    log_file_name = env+".json"
    csv_file_name = env+".csv"
    with open(log_file_name, "w") as file:
        json.dump(r.text, file)
    temp_file_name = convert_json_csv(json_file_path='log_file_name', csv_file_path=csv_file_name, search_key='value')
    send_logs_to_bds(csv_file_to_send='temp_file_name')

    return 'Completed'

if __name__ == '__main__':
    keys = {'lab': 'xxxxxxxxxxxxxx', 'mgmt': 'xxxxxxxxxxxxxx', 'nonprod': 'xxxxxxxxxxx'}
    threads = []
    for x,y in keys.items():
        t = threading.Thread(target=main(x,y))
        threads.append(t)
        t.start()
