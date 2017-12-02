#######################################################
#!/usr/bin/python                                     #
# Author: Vijay Singh Gosai                           #
# Date: 03-30-2015                                    #
# Purpose: Status Check Script to check node services #
#######################################################
import os,time,sys
import subprocess
import string

p = subprocess.Popen("netstat -ntlp".split(), stdout=subprocess.PIPE).stdout
grep = subprocess.Popen(["egrep", ":80 | httpd"], stdin=p, stdout=subprocess.PIPE).stdout
httpd = grep.read().split("\n")
vals = map(string.strip, httpd[0].split())

if len(vals) and vals[-2] in ("LISTENING", "LISTEN"):
        print "Status OK - Apache is running.";
        sys.exit()
else:
    print "Status Not'OK - Apache is not running."
    for i in range(10,0,-1):
        print "Starting Apache:", i
        time.sleep(1)
start = os.system("/etc/init.d/apache0 start")
print "Apache Started."

Collage ERP Project on PHP.
