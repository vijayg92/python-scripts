#!/usr/bin/env python2.6

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
opt_parser.add_option("-t", "--timeout", dest="timeout", default=10, type=int, help="How many seconds to wait for host to respond.")
args = opt_parser.parse_args()[0]

if args.server == None:
  print "A Redis server (--server) must be supplied. Please see --help for more details."
  sys.exit(-1)

### Connection Call ###
try:
  if args.password is not None:
    redis_connection = redis.Redis(host=args.server, port=int(args.port), password=args.password, socket_timeout=args.timeout)
  else:
    redis_connection = redis.Redis(host=args.server, port=int(args.port), socket_timeout=args.timeout)
  redis_info = redis_connection.info()
  print(redis_info)
except (socket.error, redis.exceptions.ConnectionError, redis.exceptions.ResponseError), e:
  print "CRITICAL: Problem establishing connection to Redis server %s: %s " % (str(args.server), str(repr(e)))
  sys.exit(EXIT_NAGIOS_CRITICAL)

#### Redis Replication Status ####
pid = redis_info["process_id"]
role = redis_info["role"]
#sync = redis_info["master_last_io_seconds_ago"]

if os.path.exists('/proc/%d/status' % pid) #and sync > 0:
    print "OK: Redis %s Server %d is Running and in SYNC !!!" % (role, pid)
    sys.exit(EXIT_NAGIOS_OK)
else:
    print "CRITICAL: Redis %s Server %d is Down and out of SYNC!!!" % (role, pid)
    sys.exit(EXIT_NAGIOS_CRITICAL)

sys.exit(EXIT_NAGIOS_OK)
