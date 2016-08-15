#!/bin/bash

logfile=ircdoorbot.log

cd /root/ircdoorbot

# Append date to logfile to see when it was started
date -Iseconds >> $logfile

while true; do
    # Use -u to use unbuffered (raw) output (needed for logfile!)
    python -u ircdoorbot.py
    echo "Script crashed with exit code $?. Respawning..." >&1
    sleep 30
done >> $logfile 2>&1
