# Author :  Vijay Singh Gosai
# Version: 1.0.0

import boto3
import logging
import json
import gzip
import urllib
import time
from StringIO import StringIO

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucketS3 = 's3-rsyslogs'
    folderS3 = time.strftime('%Y-%m-%d')
    prefixS3 = folderS3+"_"
    outEvent = str(event['awslogs']['data'])
    outEvent = gzip.GzipFile(fileobj=StringIO(outEvent.decode('base64','strict'))).read()
    cleanEvent = json.loads(outEvent)

    print "Creating folder to upload logs...."
    putResponse = s3.put_object(Bucket=bucketS3, Key=folderS3 + '/')
    print putResponse

    tempFile = open('/tmp/file', 'w+')
    key = folderS3 + '/' + prefixS3 + str(int(time.time())) + ".log"

    for t in cleanEvent['logEvents']:
        #tempFile.write("t " + str(t['timestamp']) + " m " + str(t['message']) + "\n")
        tempFile.write(str(t['message']) + "\n")
    tempFile.close()
    s3Results = s3.upload_file('/tmp/file', bucketS3, key)
    print s3Results
