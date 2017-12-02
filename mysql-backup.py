#!/usr/bin/python
 
#Author: Andrew McDonald andrew@mcdee.com.au http://mcdee.com.au
 
# Example: config file
#[client]
#host = localhost
#user = root
#password = root-pass
 
from datetime import datetime
import sys, os, subprocess, tarfile
 
def print_usage(script):
    print 'Usage:', script, '--cnf <config file>', '--todir <directory>'
    sys.exit(1)
 
def usage(args):
  if not len(args) == 5:
    print_usage(args[0])
  else:
    req_args = ['--cnf', '--todir']
    for a in req_args:
      if not a in req_args:
        print_usage()
      if not os.path.exists(args[args.index(a)+1]):
        print 'Error: Path not found:', args[args.index(a)+1]
        print_usage()
  cnf = args[args.index('--cnf')+1]
  dir = args[args.index('--todir')+1]
  return cnf, dir
 
def mysql_dblist(cnf):
  no_backup = ['Database', 'information_schema', 'performance_schema', 'test']
  cmd = ['mysql', '--defaults-extra-file='+cnf, '-e', 'show databases']
  p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  stdout, stderr = p.communicate()
  if p.returncode > 0:
    print 'MySQL Error:'
    print stderr
    sys.exit(1)
  dblist = stdout.strip().split('\n')
  for item in no_backup:
    try:
      dblist.remove(item)
    except ValueError:
      continue
  if len(dblist) == 1:
    print "Doesn't appear to be any user databases found"
  return dblist
 
def mysql_backup(dblist, dir, cnf):
  for db in dblist:
    bdate = datetime.now().strftime('%Y%m%d%H%M')
    bfile =  db+'_'+bdate+'.sql'
    dumpfile = open(os.path.join(dir, bfile), 'w')
    if db == 'mysql':
      cmd = ['mysqldump', '--defaults-extra-file='+cnf, '--events', db]
    else:
      cmd = ['mysqldump', '--defaults-extra-file='+cnf,  db]
    p = subprocess.Popen(cmd, stdout=dumpfile)
    retcode = p.wait()
    dumpfile.close()
    if retcode > 0:
      print 'Error:', db, 'backup error'
    backup_compress(dir, bfile)
 
def backup_compress(dir, bfile):
  tar = tarfile.open(os.path.join(dir, bfile)+'.tar.gz', 'w:gz')
  tar.add(os.path.join(dir, bfile), arcname=bfile)
  tar.close()
  os.remove(os.path.join(dir, bfile))
 
def main():
  cnf, dir = usage(sys.argv)
  dblist = mysql_dblist(cnf)
  mysql_backup(dblist, dir, cnf)
 
if __name__ == '__main__':
  main()