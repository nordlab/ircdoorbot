#!/bin/bash

cd /root/ircdoorbot
until python ircdoorbot.py; do
    echo "Server 'myserver' crashed with exit code $?. Respawning..." >&2
    sleep 30
done
