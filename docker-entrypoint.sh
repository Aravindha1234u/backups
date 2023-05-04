#!/bin/sh

echo "$CRON backup /opt/backups/backup.cfg" >> /etc/crontabs/root
crontab -l
crond -f -l 2 -L /dev/stdout