import boto3
import botocore

ec2 = boto3.client('ec2')
r53 = boto3.client('route53')

def check_dns_zone(zone_name):
    id = ''
    list_zones = r53.list_hosted_zones()
    try:
        for zone in list_zones['HostedZones']:
            if zone_name in zone['Name']:
                id = zone['Id']
            else:
                print("Unable to find Hosted Zone entry for %s" % (zone['Name']))
    except Exception as err:
        print(err)
    else:
        return id

def get_instance_name(inst_id):
    inst_name = ''
    ec2 = boto3.resource('ec2')
    ec2instance = ec2.Instance(inst_id)
    for tags in ec2instance.tags:
        if tags["Key"] == 'Name':
            inst_name = tags["Value"]
    if inst_name[-1] != ".":
        inst_name = inst_name + '.'
    return inst_name

def create_dns_records(zone_id, name, value):
    try:
        response = r53.change_resource_record_sets(
            HostedZoneId=zone_id,
            ChangeBatch= {
                'Changes': [
                    {
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': name,
                            'Type': 'A',
                            'TTL': 300,
                            'ResourceRecords': [{'Value': value}]
                        }
                    },
                    {
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': name,
                            'Type': 'TXT',
                            'TTL': 300,
                            'ResourceRecords': [{'Value': '"' + value + '"'}]
                        }
                    }
                ]})
    except botocore.exceptions.ClientError as err:
        print(err)
    else:
        return response

def validate_instances():
    name, ip, zone_id = '', '', ''
    ec2_list = ec2.describe_instances()    
    for x in ec2_list['Reservations']:
        for y in x['Instances']:
            for z in range(len(y['Tags'])):
                if "Environment" in y['Tags'][z]['Key']:
                    zone_id = check_dns_zone(y['Tags'][z]['Value'])
                    ip = y['PrivateIpAddress']
                    name = get_instance_name(y['InstanceId'])
                    print(name, ip, zone_id)
    return create_dns_records(zone_id, name, ip)
                                    

if __name__ == '__main__':
    ec2_check = validate_instances()
