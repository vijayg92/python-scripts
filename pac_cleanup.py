#!/usr/bin/env python2.7
# Author :  Vijay Singh Gosai
# Version: 1.0.0
### Importing python modules ###
import os, time, datetime, sys, glob, logging, shutil

### Global Variables ###
pacfiles_dir = '/appl/pacData/'
date_time = time.strftime('%m-%d-%Y')
logfile = '/logs/pacfile_bakeup.log'
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(logfile)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

### To check wheather backupdir exists or not ###
def check_backup_dir(dir_name):
    logger.info("Checking Backup Directory Path!!!")
    if os.path.isdir(dir_name):
        logger.debug("Root BackupDir %s is already exist !!!" % dir_name)
        pacBackupDir = dir_name + date_time
        if not os.path.exists(pacBackupDir):
            pacBackupDir = dir_name + date_time
            logger.info("Creating pacfiles Backup Directory %s !!!" % pacBackupDir)
            os.makedirs(pacBackupDir)
            logger.debug("Pacfile BackupDir %s has been created sucessfully !!!" % pacBackupDir)
    else:
        logger.info("Checking Backup Directory Path!!!")
        if not os.path.exists(dir_name):
            logger.info("Creating Root Backup Directory %s !!!" % dir_name)
            os.makedirs(dir_name)
            logger.debug("Root Backup Directory %s has been created sucessfully" % dir_name)
            pacBackupDir = dir_name + date_time
            if not os.path.exists(pacBackupDir):
                logger.info("Creating pacfile Backup Directory %s !!!" % pacBackupDir)
                os.makedirs(pacBackupDir)
                logger.debug("Pacfile BackupDir %s has been created sucessfully" % pacBackupDir)

### To take backup of pacfiles ###
def copy_pacfiles(srcDir, destDir):
    destDir = destDir + date_time
    if os.path.isdir(srcDir) and os.path.isdir(destDir):
        logger.info("Starting backup of pacfiles !!!")
        count = 0
        for pacfile in glob.glob(os.path.join(srcDir, '*.pac')):
            shutil.copy2(pacfile, destDir)
            count=count+1
        logger.debug("Copied %i number of pacfiles !!!" % count)
        logger.info("Archiving pacfile backup directory %s  !!!" % destDir)
        shutil.make_archive(destDir,'gztar',srcDir)
        logger.info("Pacfile directory has been sucessfully acrchived !!!")
    else:
        logger.error("Either Source or Destination %s Path doesn't exists !!!" % destDir)
        sys.exit(1)

### To match pacfile from net.data files ###
def match_pacfile(netdata_path):
    for file in open(netdata_path, 'r'):
        columns = file.split("=")
        columns = [col.strip() for col in columns]
        check_file_path = pacfiles_dir + columns[-1]
        if os.path.exists(check_file_path):
            logger.info("File %s does exists !!!" % check_file_path)
        else:
            logger.info("File %s doesnot exist in net.data hence removing this file !!!" % check_file_path)
            os.remove(check_file_path)
            logger.debug("File %s has been purged !!!" % check_file_path)

if __name__ == '__main__':
    logger.info("=========== Starting Backup %s =====================" % date_time)
    check_backup_dir('/appl/backup_pac/')
    copy_pacfiles('/appl/pacData/', '/appl/backup_pac/')
    match_pacfile('/appl/pacData/net.data')
    logger.info("=========== Backup has been completed !!! =====================")
