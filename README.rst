============
IRC Door Bot
============

A simple IRC bot for posting the door (un)locks and some simple statistics
(how long opened/closed) in an IRC channel.

Configuration
=============

Move :code:`config.py.example` to :code:`config.py` and edit it.

Testing
=======

- Install an IRC daemon like `UnrealIRCd <https://www.unrealircd.org/>`_
- Run :code:`test/spaceapi-server.py` which serves a simple HTTP server on port 8001 by
  default and simulates a the `Space API <http://spaceapi.net/>`_ for a hackerspace
- Set up ircdoorbot (see "Configuration") and run :code:`ircdoorbot.py`
- Write "opened" or "closed" into :code:`status.txt` to simulate the door state
  (e.g. via :code:`echo opened > test/status.txt`)
