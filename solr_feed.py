#!/usr/bin/env python2.7
# Author :
# Version: 1.0.0

import sys, getopt, pysolr, csv, json
from optparse import OptionParser

class SolrFeed(object):

    def __init__(self, server='http://localhost:8983/solr/', filename):

        self.server = server
        self.filename = filename

    def feed_data(self.filename):

        keys=("rank", "pogid", "cat", "subcat", "question_bucketid", "brand", "discount", "age_grp", "gender", "inventory",   "last_updated")
        record_count=0

        try:
            solr = pysolr.Solr(self.server, timeout=10)
            try:
                for line in open(self.filename, 'r').readlines():
                    splits = line.split(',')
                    record_count += 1
                    # add record for indexing
                    items=[{"id":record_count, "rank":splits[0], "pogid":splits[1], "cat":splits[2], "subcat":splits[3],   "question_bucketid":splits[4], "brand":splits[5], "discount":splits[6], "age_grp":splits[7], "gender":splits[8],   "inventory":splits[9], "last_updated":splits[10]}]

                solr.add(items, commit=True)
                solr.commit()
                print 'Data has been Sucessfully addedd!!'

            except IOError as error:
                print error

        except SolrError as error:
            print error

if __name__ == '__main__':
    parser = OptionParser(usage="Usage: %prog [options]", version="%prog 1.0")
    parser.add_option("-s", "--server", dest="server", default="http://localhost:8983/solr/", help="Solar Server")
    parser.add_option("-f", "--file", dest="file", help="Input file", metavar="FILE")
    (options, args) = parser.parse_args()

    for i in "server file".split():
        if options.__dict__[i] is None:
            parser.error("Parameter Error !!! %s is required" %i)
            sys.exit(-1)

    s = SolrFeed(options.server, options.file)
    print s.feed_data()
