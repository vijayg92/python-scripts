#!/usr/bin/env python3

import boto3, json, os, sys
from optparse import OptionParser

def main(access_key, secret_key):
    client = boto3.client('ec2', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name='us-east-1')
    ec2_regions = [region['RegionName'] for region in client.describe_regions()['Regions']]

    for region in ec2_regions:
        conn = boto3.resource('ec2', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region)
        instances = conn.instances.filter()
        for instance in instances:
            if instance.state["Name"] == "running":
                print("InstanceID: %s, InstanceType: %s, Region: %s, Tag: %s\n" % (instance.id, instance.instance_type, region, instance.tags))

if __name__ == '__main__':
    parser = OptionParser(usage="Usage: %prog [options]", version="%prog 1.0")
    parser.add_option("-a", "--access-key", dest="akey", help="AWS Access Key")
    parser.add_option("-s", "--secret-key", dest="skey", help="AWS Secret Key")
    (options, args) = parser.parse_args()

    for i in "akey skey".split():
        if options.__dict__[i] is None:
            parser.error("Parameter Error !!! %s is required" %i)
            sys.exit(-1)
    main(options.akey, options.skey)
