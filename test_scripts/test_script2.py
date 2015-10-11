#!/usr/bin/python
import sys
sys.path.append('/home/devops/rsync_snapshot_scripts/rsync_snapshot_common')

from rsync_snapshot_common import *

#/var/lib/ - testing 2 level directory.
backup_params = { 'remote_user':   'devops',
                      'remote_server': 'example1.cloudapp.net',
                      'ssh_port': '2222',
                      'remote_dir': '/var/log/', #note the trailing slash is important.
                      'backup_location': '/backups-static/test/backup-server-1/',
                      'max_num_backups': 5
                    }

do_rsync_backup(backup_params)


#/var/lib/ - testing a failure case, the remote is not contactable.
backup_params = { 'remote_user':   'devops',
                  'remote_server': 'example1.cloudapp.net',
                  'ssh_port': '3333',
                  'remote_dir': '/var/lib/', #note the trailing slash is important.
                  'backup_location': '/backups-static/test/backup-server-1/',
                  'max_num_backups': 5
                    }

do_rsync_backup(backup_params)

#/var/spool/postfix/  - testing 3rd level directories.
backup_params = { 'remote_user':   'devops',
                  'remote_server': 'example1.cloudapp.net',
                  'ssh_port': '2222',
                  'remote_dir': '/var/spool/postfix/', #note the trailing slash is important.
                  'backup_location': '/backups-static/test/backup-server-1/',
                  'max_num_backups': 5
                    }

do_rsync_backup(backup_params)


#/var/spool/cron  - testing behavior without trailing slash.
backup_params = { 'remote_user':   'devops',
                  'remote_server': 'example1.cloudapp.net',
                  'ssh_port': '2222',
                  'remote_dir': '/var/spool/cron', #note the trailing slash is important.
                  'backup_location': '/backups-static/test/backup-server-1/',
                  'max_num_backups': 5
                    }

do_rsync_backup(backup_params)
