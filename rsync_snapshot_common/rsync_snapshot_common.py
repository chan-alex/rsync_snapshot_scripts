#!/usr/bin/python

# The code implement rsync hard-link style backup with the --link-dest option.
# Attempts to do the rsync of a remote directory to a local directory.
# It will keep previous (default is specified by EFAULT_NUM_OF_BACKUPS_TO_KEEP copies of the remote directory
# See http://www.mikerubel.org/computers/rsync_snapshots/ for the theory.

import os
import sys
import platform
import os.path
import errno
import uuid
import shutil
import subprocess
from glob import glob
from datetime import datetime


#modules for sending emails.
import smtplib
from email.mime.text import MIMEText




RSYNC_BASE = '/usr/bin/rsync -avzP --delete --numeric-ids --rsync-path="sudo rsync" --delete --numeric-ids --timeout=120'  
SSH_OPTS = "ssh -i /root/.ssh/devops_key -o ConnectTimeout=20 "   # this is where the devops key is specified
DEFAULT_NUM_OF_BACKUPS_TO_KEEP=5
TEMP_DIR = '/tmp'
EMAIL_ADDRESSES = ["alex.chan@example.com"]



def generate_base_rsync_cmd(backup_params):

  # -e "ssh -i /root/.ssh/devops_key -p 22"
  ssh_opts = '-e "' + SSH_OPTS + ' -p ' + str(backup_params['ssh_port']) + '"'
  #print "ssh options: " + ssh_opts

  # devops@dev-other1.cloudapp.net:/etc/   note: the trailing slash is important. left to use to specifiy correctly.
  rsync_source = backup_params['remote_user'] + '@' +  backup_params['remote_server'] + ':' + backup_params['remote_dir']
  #print "rsync_source: " + rsync_source

  # /backups-static/test/dev-other1/etc/etc-20151002 
  date_time_now = datetime.now().strftime('%Y%m%d%H%M')
  backup_path = os.path.join(backup_params['backup_location'], backup_params['remote_dir'].strip('/'))
  backup_params['backup_path'] = backup_path
  backup_params['backups_search_path'] = backup_path + '*'
  backup_params['actual_backup_location'] = backup_path + '-' + date_time_now
  #print "actual_backup_location: " + backup_params['actual_backup_location']


  #temp logfile for rsync to log information to. e.g. /tmp/rsync-4e77d7eb-b5d8-4939-bbad-6841821930d4.log
  log_filename = "rsync-" + str(uuid.uuid4()) + '.log'
  log_filename = os.path.join(TEMP_DIR,log_filename)
  backup_params['logfile']= log_filename   # save for later use.
  logfile_opt = "--log-file=" + log_filename
  #print   "logfile opts: " + log_filename

  rsync_cmd = ' '.join([RSYNC_BASE, ssh_opts, rsync_source, backup_params['actual_backup_location'], logfile_opt])


  # this section is for setting up the --link-dest configuration. Important for icremental backups.
  latest_backup = find_latest_backup(backup_params)
  if latest_backup and latest_backup != backup_params['actual_backup_location']:
    link_dest_opt = "--link-dest=" + latest_backup
    rsync_cmd = rsync_cmd + ' ' +  link_dest_opt


  backup_params['rsync_cmd'] = rsync_cmd   # saving incase useful.
  return rsync_cmd


def find_latest_backup(backup_params):

  found = glob(backup_params['backups_search_path'])
  if len(found) > 0: 
    
    #sort in descending order. This is an in place sort.
    found.sort(reverse=True)
    #The first one is the latest backup.
    latest_backup = found[0]
    return latest_backup

  else:
  
    return ''




def cleanup(backup_params):
  # cleanup backup location becasue it could be incomplete.
  if os.path.isdir(backup_params['actual_backup_location']):
    print "Attempting to delete " + backup_params['actual_backup_location']
    shutil.rmtree(backup_params['actual_backup_location'], ignore_errors=True)

  # clean the temporary logfile
  if os.path.isfile(backup_params['logfile']):
    print "Attempting to delete temp logfile:" + backup_params['logfile']
    os.remove(backup_params['logfile'])



def purge_old_backups(backup_params):
   # keep the last num number of backups.
  
  num_of_backups_to_keep = DEFAULT_NUM_OF_BACKUPS_TO_KEEP
  if 'max_num_backups' in backup_params:
    num_of_backups_to_keep = int(backup_params['max_num_backups'])

  #print "number of backups to keep: " + str(num_of_backups_to_keep)

  found = glob(backup_params['backups_search_path'])

  if len(found) == 0:
    print "Apparently there are no backups found. nothing to purge."
    return 


  # sort in descending order. This is an in place sort.
  # if the directories were named correctly, this results in the latest backup dir in the beginning.
  # The older ones are at the back which are the ones to delete.
  found.sort(reverse=True)
  to_delete = found[num_of_backups_to_keep:]
  for d in to_delete:
    print "Deleting " + d + "..."
    shutil.rmtree(d, ignore_errors=True)



def send_email_notification(mail_error_text):

  mail_text = "Hi,\n"
  mail_text += "This email was generated during the running of this script: \"" + os.path.basename(sys.argv[0]) + "\" "
  mail_text += "on server \"" + platform.node() + '\". \n'
  mail_text += mail_error_text
  msg = MIMEText(mail_text)

  #msg['Subject'] = 'Rsync script email notification'
  msg['Subject'] = 'A Rsync snapshot backup of static server failed.'
  #msg['To'] = EMAIL_ADDRESSES

  try:
    s = smtplib.SMTP('localhost')
    s.sendmail( "rsync-script", EMAIL_ADDRESSES, msg.as_string())
    s.quit()
  except smtplib.SMTPException as error:
    print "Error: unable to send email :  {err}".format(err=error)
  except :
    print "An error occurred while trying to send email. The SMTP server could be down or uncontactable."


# note: best not use the create_backup_location() method.
def create_backup_location(backup_params):

  backup_location =  backup_params['actual_backup_location']
  print "Checking if " +  backup_location + " exists."

  if os.path.exists(backup_location):
    print "It already exists, continuing."
  else:   
    print "Attemping to create directory..."

    try:
       os.makedirs(backup_location)
    except OSError as e:
      if e.errno == errno.EEXIST:
        print "The directory appears have been created." 
      elif e.errno == errno.EACCES:
        print "Permission denied. You probably need to run this script as another user."
      else:
        print "There was an unexpected error while creating the directory. Not continuing."
        raise e
      
      return False
    
    return True


def do_rsync_backup(backup_params):
  #generate initial rsync command.
  rsync_cmd = generate_base_rsync_cmd(backup_params)

  #attempt to create the backup location if it does not exist,
  #create_backup_location(backup_params)  # don't use too unsafe.

  # this section executes the rsync command./
  print "\n Attmepting to execute: " + rsync_cmd + "\n"
  try:
      out_bytes = subprocess.check_output(rsync_cmd,shell=True)
  except subprocess.CalledProcessError as e:
      #out_bytes = e.output # Output generated before error 
      code = e.returncode # Return code
      print "There was an error when the rsync command was executued. Error code was: " + str(code)
      
      print "Doing cleanup..."
      cleanup(backup_params)

      print "Sending an email notification..."
      error_msg = "Error: There was a problem executing the following rsync command: \n"
      error_msg += e.cmd + '\n'
      error_msg += "The error code was: " + str(e.returncode)

      send_email_notification(error_msg)
      return  #just exit if rsync fails.


  print "Rsync executed with no errors. Continuing."

  #moving logfile to backup location for further reference.
  print "Moving rsync logfile (" + backup_params['logfile'] +") to " + backup_params['actual_backup_location'] + "."
  shutil.move(backup_params['logfile'], backup_params['actual_backup_location'])

  #this section is for creating the "latest" symlink for easy searching.
  #symlink =  os.path.dirname(backup_params['actual_backup_location']) + "/latest"  
  #print 'creating the \"latest\" symlink... ' + symlink
  #if os.path.islink(symlink): 
  #  os.unlink(symlink)
  #os.symlink(backup_params['actual_backup_location'],  symlink)


  # purge older backups.
  print "Checking for any old backups to delete..."
  purge_old_backups(backup_params) 


if __name__ == "__main__":


#from backup_common import *


  #backup_params = { 'remote_user':   'devops',
  #                  'remote_server': 'dev-other1.cloudapp.net',
  #                  'ssh_port': '2222',
  #                  'remote_dir': '/etc/',
  #                  'backup_location': '/backups-static/test/dev-other1/etc/',
  #                  'max_num_backups': 5
  #                  }

  #do_rsync_backup(backup_params)

  send_email_notification("test 123 123. This is a test email, please ignore.")
