#!/usr/bin/python

import sys
sys.path.append('/home/devops/rsync_snapshot_scripts/rsync_snapshot_common')

from rsync_snapshot_common import *


etc_backup_params = { 'remote_user':   'devops',
                      'remote_server': 'example.com.sg',
                      'ssh_port': '54419',
                      'remote_dir': '/etc/',
                      'backup_location': '/backup-static/rsync-snapshot/SG/etc/',
                      'max_num_backups': 7
                  }

do_rsync_backup(etc_backup_params)

data_backup_params = { 'remote_user':   'devops',
                       'remote_server': 'example.com.sg',
                       'ssh_port': '54419',
                       'remote_dir': '/data/',
                       'backup_location': '/backup-static/rsync-snapshot/SG/data/',
                       'max_num_backups': 7
                    }

do_rsync_backup(data_backup_params)



