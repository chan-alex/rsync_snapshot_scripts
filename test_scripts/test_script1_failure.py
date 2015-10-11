#!/usr/bin/python
import sys
sys.path.append('/home/devops/rsync_snapshot_scripts/rsync_snapshot_common')


from rsync_backup_common import *

etc_backup_params = { 'remote_user':   'devops',
                      'remote_server': 'example1.cloudapp.net',
                      'ssh_port': '222',
                      'remote_dir': '/etc/',
                      'backup_location': '/backups-static/test/backup-server-1/etc/',
                      'max_num_backups': 5
                    }

do_rsync_backup(etc_backup_params)



