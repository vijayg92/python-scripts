#!/usr/bin/env python

import sys, os, socket, struct
import redis
from optparse import OptionParser

# Constants
EXIT_NAGIOS_OK = 0
EXIT_NAGIOS_WARN = 1
EXIT_NAGIOS_CRITICAL = 2

# Command line options
opt_parser = OptionParser()
opt_parser.add_option("-s", "--server", dest="server", help="Redis server to connect to.")
opt_parser.add_option("-p", "--port", dest="port", default=6379, help="Redis port to connect to. (Default: 6379)")
opt_parser.add_option("-P", "--password", dest="password", default=None, help="Redis password to use. Defaults to unauthenticated.")
opt_parser.add_option("-w", "--warn", dest="warn_threshold", help="Memory utlization (in MB) that triggers a warning status.")
opt_parser.add_option("-c", "--critical", dest="critical_threshold", help="Memory utlization (in MB) that triggers a critical status.")
opt_parser.add_option("-t", "--timeout", dest="timeout", default=10, type=int, help="How many seconds to wait for host to respond.")
args = opt_parser.parse_args()[0]

if args.server == None:
  print "A Redis server (--server) must be supplied. Please see --help for more details."
  sys.exit(-1)

# can't check /proc unless on local
# (local routable IP addresses not accounted for)
is_local = args.force_local or (args.server in ['127.0.0.1','localhost','::1'])

args_dict = args.__dict__
for option in check_fields:
    if args_dict[option] == None:
        print "A %s %s must be supplied. Please see --help for more details." % tuple(option.split("_"))
        sys.exit(-1)

    try:
      value = (args.__dict__[option])
      if value < 0: raise ValueError
      else: globals()[option] = int(value)
    except ValueError, e:
      print  "A %s %s must be a positive integer. Please see --help for more details." % tuple(option.split("_"))
      sys.exit(-1)

# ================
# = Nagios check =
# ================

# Connection
try:
  if args.password is not None:
    redis_connection = redis.Redis(host=args.server, port=int(args.port), password=args.password, socket_timeout=args.timeout)
  else:
    redis_connection = redis.Redis(host=args.server, port=int(args.port), socket_timeout=args.timeout)
  redis_info = redis_connection.info()
except (socket.error, redis.exceptions.ConnectionError, redis.exceptions.ResponseError), e:
  print "CRITICAL: Problem establishing connection to Redis server %s: %s " % (str(args.server), str(repr(e)))
  sys.exit(EXIT_NAGIOS_CRITICAL)


# Redis memory usage

if redis_info["used_memory"] / 1024 / 1024 >= critical_threshold:
  print "CRITICAL: Redis is using %dMB of RAM." % (redis_info["used_memory"] / 1024 / 1024)
  sys.exit(EXIT_NAGIOS_CRITICAL)
elif redis_info["used_memory"] / 1024 / 1024 >= warn_threshold:
  print "WARN: Redis is using %dMB of RAM." % (redis_info["used_memory"] / 1024 / 1024)
  sys.exit(EXIT_NAGIOS_WARN)

# RSS memory usage
if is_local:
  try:
    pid = redis_info["process_id"]
    rss = int(open('/proc/%d/status' % pid).read().split('\n')[15].split()[1]) / 1024
  except IOError, e:
    print "CRITICAL: can't open /proc/%d/status" % pid
    sys.exit(EXIT_NAGIOS_CRITICAL)

  sys.exit(EXIT_NAGIOS_OK)
