#!/usr/bin/env python2.7

import os, sys, argparse, logging

from boto.s3 import connect_to_region
from boto.s3.connection import S3Connection, OrdinaryCallingFormat
from boto.s3.key import Key

class SyncS3():
	
    def __init__(self, key, secret, bucket, region, dfolder):
        '''
        Initialize AWS Credentials
        '''
	self.key = key
	self.secret = secret
	self.bucket = bucket
	self.region = region
	self.dfolder = dfolder

    def get_s3_bucket(self):
        '''
        Create an S3 connection to the bucket
        '''
        if self.region is None:
            conn = S3Connection(self.key, self.secret)
        else:
            # Bucket names with '.' need special treatment
            if '.' in self.bucket:
                conn = connect_to_region(
                    self.region,
                    aws_access_key_id=self.key,
                    aws_secret_access_key=self.secret,
                    calling_format=OrdinaryCallingFormat())
            else:
                conn = connect_to_region(
                    self.region,
                    aws_access_key_id=self.key,
                    aws_secret_access_key=self.secret)

        return conn.get_bucket(self.bucket)


    def sync_log_files(self, prefix=None):
        '''
        Download all log files which aren't on the disk already
        '''
        # Make sure the download folder exists
	if not os.path.exists(os.path.join(self.dfolder)):
	   	os.mkdir(os.path.join(self.dfolder))
        	if not os.path.exists(os.path.join(self.dfolder, prefix)):
            		os.mkdir(os.path.join(self.dfolder, prefix))

        for key in self.get_s3_bucket().list(prefix=prefix):
            key_str = str(key.key)

            # check if file exists locally otherwise download
            if not os.path.exists(os.path.join(self.dfolder, key_str)):
                key.get_contents_to_filename(os.path.join(self.dfolder, key_str))
                print key_str

if __name__=='__main__':

	parser = argparse.ArgumentParser(description='Sync S3 bucket files to the local file system')
	parser.add_argument('--key', help='S3 Access Key', required=True, type=str)
	parser.add_argument('--secret', help='S3 Access Secret', required=True, type=str)
	parser.add_argument('--bucket', help='S3 Bucket Name', type=str, required=True)
	parser.add_argument('--region', help='S3 Region of bucket', default="ap-south-1", type=str)
	parser.add_argument('--folder', help='Folder within your S3 Bucket', required=True, type=str)
	parser.add_argument('--target', help='Local folder to dump S3 files', default="/tmp/s3dump/",  type=str)

	args = vars(parser.parse_args())

	logging.basicConfig(filename="/tmp/s3download.logs", level=logging.INFO)
	syncer = SyncS3(args['key'], args['secret'], args['bucket'], args['region'], args['tfolder'])
	syncer.sync_log_files(prefix=args['dfolder'])
	logging.info('Sync for the bucket ' + args['bucket'] + ' completed.')
	sys.exit()
