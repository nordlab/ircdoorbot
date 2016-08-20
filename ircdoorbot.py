#!/usr/bin/env python3

import urllib.request
import json
import time
import threading
import os
import sys

from irc import *
from config import *

def doorstate():
	spaceApiUri = "{}".format(SPACEAPIURI)
	result = None

	with urllib.request.urlopen(spaceApiUri) as c:
		result = c.read().decode("utf-8")

	spaceApi = json.loads(result)

	return (spaceApi["state"]["open"], spaceApi["state"]["lastchange"])

def checkdoor(irc, interval):
	try:
		laststate, lastchanged = doorstate()

		while True:
			state, changed = doorstate()
			#print("Checking door state: {} (was {})".format(state, laststate))

			if state != laststate:
				print("Door status changed!")
				os.environ['TZ'] = "{}".format(TIMEZONE)
				time.tzset()
				changetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(lastchanged))
				t = time.mktime(time.localtime()) - time.mktime(time.localtime(lastchanged))
				changeduration = "{} Tagen {} Stunden, {} Minuten und {} Sekunden".format(
					int(t // (24 * 3600)),
					int(t // 3600),
					int(t % 3600 // 60),
					int(t % 60)
				)

				if state:
					irc("NOTICE", "{}".format(CHANNEL), ":{} ist offen (war seit dem {} für {} geschlossen)\r\n".format(SPACENAME, changetime, changeduration))
					irc("TOPIC", "{}".format(CHANNEL), ":{} ist OFFEN seit {} || {}\r\n".format(SPACENAME, changetime, TOPIC))
				else:
					irc("NOTICE", "{}".format(CHANNEL), ":{} ist geschlossen (war seit dem {} für {} geöffnet)\r\n".format(SPACENAME, changetime, changeduration))
					irc("TOPIC", "{}".format(CHANNEL), ":{} ist GESCHLOSSEN seit {} || {}\r\n".format(SPACENAME, changetime, TOPIC))
				laststate = state
				lastchanged = changed

			time.sleep(interval)
	except:
		excType, excValue, excTraceback = sys.exc_info()
		print(excValue, file=sys.stderr)

def loggedin(irc, *args):
	ircc("JOIN", "#hackerspace")

def joined(irc, *args):
	doorchecker = threading.Thread(target=checkdoor, args=(irc, CHECKINTERVAL))
	doorchecker.daemon = True
	doorchecker.start()

if __name__ == "__main__":
	try:
		ircc = IRC()
		ircc.connect(HOST, PORT)
		ircc("NICK", NICK)
		ircc("USER", USER, HOST, "*", ":{}".format(REALNAME))

		ircc.registerCallback("loggedin", loggedin)
		ircc.registerCallback("joined", joined)

		ircc.start()
	finally:
		print("Disconnecting...")
		ircc.disconnect()
