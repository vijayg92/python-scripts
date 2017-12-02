#!/usr/bin/env python3

import os, csv, sys
from datetime import date, timedelta
from optparse import OptionParser

class ScanCSV(object):

    yesterday = "2017/05/09"
    #yesterday = date.today() - timedelta(1)

    def __init__(self, source_dir, input_file, output_file):

        self.source_dir = source_dir
        self.input_file = input_file
        self.output_file = output_file
        try:
            if not os.path.exists(self.source_dir):
                print("Error !! Source directory doesn't exist!")
            else:
                if not os.path.isfile(os.path.join(self.source_dir, self.input_file)):
                    print ("Error !! Inputfile doesn't exist!")
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    def parse_csv_file(self):

        ifile = os.path.join(self.source_dir, self.input_file)
        ofile = os.path.join(self.source_dir, self.output_file)

        try:
            with open(ofile, "w", newline='') as fo:
                writer = csv.writer(fo, delimiter=',')
                with open(ifile, 'rt') as fi:
                    reader = csv.reader(fi, delimiter=',')
                    row0 = next(reader)
                    row0.append('DynamicURL')
                    writer.writerow(row0)
                    for rows in reader:
                        if ScanCSV.yesterday in rows[38]:
                            dyurl = ("https://www.hpfod.com/Releases/%s/issues" % (rows[7]))
                            rows.append(dyurl)
                            writer.writerow(rows)
                fi.close()
            fo.close()
        except IOError:
            print("Unable to read the file!!")

if __name__ == '__main__':
    parser = OptionParser(usage="Usage: %prog [options]", version="%prog 1.0")
    parser.add_option("-d", "--src_dir", dest="srcdir", help="Source Directory")
    parser.add_option("-i", "--inputfile", dest="infile", help="Output File", metavar="FILE")
    parser.add_option("-o", "--outfile", dest="outfile", help="Input File", metavar="FILE")
    (options, args) = parser.parse_args()

    for i in "srcdir infile outfile".split():
        if options.__dict__[i] is None:
            parser.error("Parameter Error !!! %s is required" %i)
            sys.exit(-1)

    scan = ScanCSV(options.srcdir, options.infile, options.outfile)
    scan.parse_csv_file()
