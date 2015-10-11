# rsync_snapshot_scripts

This is a set of python scripts for making rsync incremental backups with the --link-dist option.
For the basic theory, see: http://www.mikerubel.org/computers/rsync_snapshots/index.html.

The script does a "pull" rsync. The backup server initiates a rsync on the remote server.
This makes it easier to schedule backups for multiple servers.

The user account on the remote server ("devops" in this case) should configured to able to sudo as root with no password.
This is so that it can access all directories without permissions issues.

The backup script are to be executed from crontab (as root if necesarily) like this:

  09 23  *  *  *   /home/devops/rsync_snapshot_scripts/rsync-backup-SG.py  2>&1 | /usr/bin/logger -t rsync_snapshot

This redirects the output to the syslog so you can review how the script went.



