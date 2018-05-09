import os, sys, csv, re, glob
from optparse import OptionParser

def main(jenkins_job_home,csv_path='None'):
    
    try:
        csv = open(csv_path, "w")
        header = "Job,Plugin,Status\n"
        csv.write(header)

        os.chdir(jenkins_job_home)
        for file in glob.glob('*/*.xml'):
            job_name = file.split('/')[-2]
            filepath = os.path.join(jenkins_job_home + file)
            f = open(filepath,'r')
            for l in f:
                plugin = re.findall('plugin="(...*)"\S',l)
                if plugin:
                   	row = job_name + "," + plugin[0] + "," + "Null" + "\n"
	                csv.write(row)         
    except OSError as err:
        raise err

if __name__=='__main__':
    parser = OptionParser(usage="Usage: %prog [options]", version="%prog 1.0")
    parser.add_option("-j", "--jenkins_home", dest="jenkins_home", help="Jenkins Jobs Path i.e. /var/lib/jenkins/jobs/", metavar="FILE")
    parser.add_option("-c", "--csv_path", dest="csv_path", help="CSV File path to store the output i.e. /tmp/plugins.csv", metavar="FILE")
    (options, args) = parser.parse_args()
    
    if options.jenkins_home is None:
        parser.error("Jenkins home path is required!!")
    if options.csv_path is None:
        parser.error("CSV Output path is required!!")
    list = main(options.jenkins_home, options.csv_path)
