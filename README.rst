============
IRC Door Bot
============

A simple IRC bot for posting the door (un)locks and some simple statistics
(how long opened/closed) in an IRC channel.

Configuration
=============

Move config.py.example to config.py and edit it.

Testing
=======

- Install an IRC daemon like UnrealIRCd
- Run test/spaceapi-server.py which serves a simple HTTP server on port 8001 by
  default and simulates a the Space API for a hackerspace
- Set up ircdoorbot (see "Configuration") and run ircdoorbot.py
- Write "opened" or "closed" into status.txt to simulate the door state
