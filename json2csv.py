#!/usr/bin/env python2.7

import json, csv, logging, os, sys
import logging.handlers
from optparse import OptionParser

class JSON2CSV(object):

    def __init__(self, infile, outfile, key):

        self.infile = infile
        self.outfile = outfile
        self.key = key

        try:
            if os.path.exists(self.infile):
                f = open(self.infile)
                data = json.load(f)
                f_data = data[self.key]
                f.close()

        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        else:
            new_file = open(self.outfile, 'w')
            csvwriter =  csv.writer(new_file)
            count = 0

            for i in f_data:
                if count == 0:
                    header = i.keys()
                    csvwriter.writerow(header)
                    count += 1
                csvwriter.writerow(i.values())
            new_file.close()

    def forward_logs(self, syslog_host, syslog_port):
        my_logger = logging.getLogger('MyLogger')
        my_logger.setLevel(logging.INFO)
        handler = logging.handlers.SysLogHandler(address = (syslog_host,syslog_port))
        my_logger.addHandler(handler)

        try:
            if os.path.exists(self.outfile):
                file_reader= open(self.outfile)
                read = csv.reader(file_reader)
            for row in read :
                my_logger.info(row)

        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

if __name__ == '__main__':

    parser = OptionParser(usage="Usage: %prog [options]", version="%prog 1.0")
    parser.add_option("-i", "--infile", dest="infile", help="Input File Path", metavar="FILE")
    parser.add_option("-o", "--outfile", dest="outfile", help="Output File Path", metavar="FILE")
    parser.add_option("-k", "--key", dest="key", help="Dict Key")
    parser.add_option("-H", "--host", dest="host", default="10.10.10.10", help="Syslog Host IP")
    parser.add_option("-P", "--port", dest="port", default=514, help="Syslog Port")
    (options, args) = parser.parse_args()

    for i in "infile outfile key host port".split():
        if options.__dict__[i] is None:
            parser.error("Parameter Error !!! %s is required" %i)
            sys.exit(-1)

    parse_logs = JSON2CSV(options.infile, options.outfile, options.key)
    parse_logs.forward_logs(options.host, options.port)
