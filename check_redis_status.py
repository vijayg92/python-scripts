#!/usr/bin/env python2.7
# Author: Vijay Singh G0sai
# Prog: 1.0.0

import sys, socket, os, redis
from optparse import OptionParser

class Redis(object):
    ### Constants Values ###
    EXIT_NAGIOS_OK = 0
    EXIT_NAGIOS_WARN = 1
    EXIT_NAGIOS_CRITICAL = 2
    EXIT_NAGIOS_UNKNOWN = 3

    def __init__(self,host,port,password,timeout=10,w_threshold=100,c_threshold=200):
        ''' This script is used to get Redis Connection Details !!! Kindly note that you must have to pass Hostname, Password to execute this script,
    apart from this defaul values are set for port=6379, warning_threshold=100 & critical_threshold=160'''

        self.h = host
        self.p = port
        self.passwd = password
        self.t = timeout
        self.w_threshold = w_threshold
        self.c_threshold = c_threshold

        try:
            if self.passwd is not None:
                redis_connection = redis.Redis(host=self.h, port=self.p, password=self.passwd, socket_timeout=self.t)
            else:
                redis_connection = redis.Redis(host=self.h, port=self.p, socket_timeout=self.t)
            self.redis_info = redis_connection.info()

        except redis.exceptions.ConnectionError as e:
            print "CRITICAL: Redis Host %s: %s " % (str(self.h), str(repr(e)))
            sys.exit(Redis.EXIT_NAGIOS_CRITICAL)

        except redis.exceptions.ResponseError as e:
            print "CRITICAL: Redis Host %s: %s " % (str(self.h), str(repr(e)))
            sys.exit(Redis.EXIT_NAGIOS_CRITICAL)


    def redis_server_status(self):
        pid_of_redis = self.redis_info['process_id']
        server_role = self.redis_info['role']
        try :
            if pid_of_redis is not None:
                print "OK: Redis %s %s is UP - PID: %s !!!" % (self.h, server_role, pid_of_redis)
        except :
                print "CRITICAL: Redis %s is DOWN!!!" %(self.h)
                return False
        else:
                return True

    def memory_status(self):
        try:
            usedMemory = self.redis_info['used_memory'] / 1024 /1024
        except:
            return "Error while fetching details of redis instance %s" %(self.h)
        else:
            return float(usedMemory)

    def replication_status(self):
        if self.redis_info['role'] == 'master' and self.redis_info['connected_slaves'] is not None:
            print "OK: Redis Master instance is connected with %d salve instance !!!" % (self.redis_info['connected_slaves'])
            return True
        else:
            try:
                self.redis_info['master_link_status'] == "up" and self.redis_info['master_last_io_seconds_ago'] == 0 and self.redis_info['master_sync_in_progress'] == 0
                print "OK: Redis Slave Replication is in progess!!!"
                return True
            except:
                return False

if __name__ == '__main__':
    parser = OptionParser(usage="Usage: %prog [options]", version="%prog 1.0")
    parser.add_option("-H", "--host", dest="host", default=None, help="Redis Host IP or FQDN")
    parser.add_option("-P", "--port", dest="port", type="int", default=6379, help="Redis Port i.e. 6379")
    parser.add_option("-p", "--pass", dest="password", default=None, help="Redis password")
    parser.add_option("-t", "--timeout", dest="timeout",type="int", default=10, help="Redis connection timeout")
    parser.add_option("-r", "--replication-status", dest="rstatus", action='store_true', default=False, help="To check Redis Replication Status")
    parser.add_option("-m", "--memory-status", dest="mstatus",action='store_true', default=False, help="To check Redis Memory Usages")
    parser.add_option("-s", "--server-status", dest="sstatus", action='store_true', default=False, help="To check Redis Server Status")
    parser.add_option("-w", "--warn", dest="w_threshold",type="int", default=250, help="Memory utlization (in MB) that triggers a warning status.")
    parser.add_option("-c", "--critical", dest="c_threshold",type="int", default=300, help="Memory utlization (in MB) that triggers a critical status.")
    (options, args) = parser.parse_args()

    for i in "host port password".split():
        if options.__dict__[i] is None:
            parser.error("Parameter Error !!! %s is required" %i)
            sys.exit(-1)

    r = Redis(options.host, options.port, options.password, options.timeout,options.w_threshold,options.c_threshold)
    if options.sstatus ==  True and options.rstatus is not True and options.mstatus is not True :
            if r.redis_server_status() == True:
                sys.exit(Redis.EXIT_NAGIOS_OK)
            else:
                sys.exit(Redis.EXIT_NAGIOS_CRITICAL)
    elif options.mstatus == True and options.rstatus is not True and options.sstatus is not True:
            if r.memory_status() >= r.c_threshold:
                print ("CRITICAL: Redis is using %d MB of RAM." %r.memory_status())
                sys.exit(Redis.EXIT_NAGIOS_CRITICAL)
            elif r.memory_status() >= r.w_threshold:
                print ("WARNNING: Redis is using %dMB of RAM." %r.memory_status())
                sys.exit(Redis.EXIT_NAGIOS_WARN)
            print ("OK: Redis is using %dMB of RAM." %r.memory_status())
            sys.exit(Redis.EXIT_NAGIOS_OK)
    elif options.rstatus == True and options.sstatus is not True and options.mstatus is not True:
            if r.replication_status() == False:
                print "CRITICAL: Redis Master Link is Down, Replication Error!!!"
                sys.exit(Redis.EXIT_NAGIOS_CRITICAL)
            else:
                sys.exit(Redis.EXIT_NAGIOS_OK)
    else:
            print " Kindly select one action at a time !!! Can't proceess Server Status, Memory Status as well as Replication Status at a same time !!!"
