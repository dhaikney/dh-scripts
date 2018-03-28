#!/bin/bash
alert_file="/tmp/alerts.txt"
while true
do 
echo Here we go
~/scripts/gerrit_done.py -n
gtimeout 30s sh -x $alert_file
# terminal-notifier -remove ALL
sleep 60
done
