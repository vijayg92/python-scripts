#!/usr/bin/env python2.7
# Author :
# Version: 1.0.0

import sys, os, json
import requests
from optparse import OptionParser

class RabbitMQ(object):

    ### Constant ###
    EXIT_NAGIOS_OK = 0
    EXIT_NAGIOS_WARN = 1
    EXIT_NAGIOS_CRITICAL = 2
    EXIT_NAGIOS_UNKNOWN = 3

    def __init__(self, host, user, password, domain, port, warn_threshold, critical_threshold):
        ''' This script is used to get rabbitmq_memory usage!! Kindly note that you must have to pass Hostname, UserName, Password to execute this script,
    apart from this defaul values are set for port=15672, domain=corporate.ge.com, warning_threshold=100 & critical_threshold=160'''

        self.host = host
        self.user = user
        self.password = password
        self.domain = domain
        self.port = port
        self.warn_threshold = warn_threshold
        self.critical_threshold = critical_threshold

    def getMemory (self):

        try:
            url = "http://"+self.host+"."+self.domain+":"+str(self.port)+"/api/nodes/rabbit@"+self.host +"?memory=true"
            getData = requests.get(url,auth=(self.user,self.password)).json()
            usedMemory = getData["mem_used"] / 1024 / 1024

        except requests.ConnectionError as e:
            print ("ConnectionError. Unable to connect to host  %s" %self.host)
            sys.exit(RabbitMQ.EXIT_NAGIOS_UNKNOWN)

        except requests.exceptions.RequestException as e:
            print (e)
            sys.exit(RabbitMQ.EXIT_NAGIOS_UNKNOWN)

        except:
            print("An unknown exception occured..")
            sys.exit(RabbitMQ.EXIT_NAGIOS_UNKNOWN)

        else:
            return usedMemory

if __name__ == '__main__':
    parser = OptionParser(usage="Usage: %prog [options]", version="%prog 1.0")
    parser.add_option("-H", "--host", dest="host", default=None, help="RabbitMQ Host i.e. alpcispmq822v")
    parser.add_option("-d", "--domain", dest="domain", default="corporate.ge.com", help="RabbitMQ Host i.e. corporate.ge.com")
    parser.add_option("-P", "--port", dest="port", type="int", default=15672, help="RabbitMQ Port i.e. 15672")
    parser.add_option("-u", "--user", dest="user", default="icinga", help="RabbitMQ user")
    parser.add_option("-p", "--pass", dest="password", default="icinga", help="RabbitMQ password")
    parser.add_option("-w", "--warn", dest="warn_threshold",type="int", default=250, help="Memory utlization (in MB) that triggers a warning status.")
    parser.add_option("-c", "--critical", dest="critical_threshold",type="int", default=300, help="Memory utlization (in MB) that triggers a critical status.")
    (options, args) = parser.parse_args()

    #variables="host domain port user password".split()
    for i in "host domain port user password".split():
        if options.__dict__[i] is None:
            parser.error("Parameter Error !!! %s is required" %i)
            sys.exit(-1)

    r = RabbitMQ(options.host, options.user, options.password, options.domain, options.port, options.warn_threshold, options.critical_threshold)
    mem_used = r.getMemory()

    if mem_used >= r.critical_threshold:
        print ("CRITICAL: RabbitMQ is using %d MB of RAM." %mem_used)
        sys.exit(RabbitMQ.EXIT_NAGIOS_CRITICAL)

    elif mem_used >= r.warn_threshold:
        print ("WARNNING: RabbitMQ is using %dMB of RAM." %mem_used)
        sys.exit(RabbitMQ.EXIT_NAGIOS_WARN)

    print ("OK: RabbitMQ is using %dMB of RAM." %mem_used)
    sys.exit(RabbitMQ.EXIT_NAGIOS_OK)
