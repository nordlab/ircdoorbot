#!/usr/bin/env python3

import urllib.request
import json
import time
import threading

from irc import *
from config import *

def doorstate():
	spaceApiUri = "http://spaceapi.nordlab-ev.de/"
	result = None

	with urllib.request.urlopen(spaceApiUri) as c:
		result = c.read().decode("utf-8")
	
	spaceApi = json.loads(result)

	return (spaceApi["state"]["open"], spaceApi["state"]["lastchange"])

def checkdoor(irc, interval):
	laststate, lastchanged = doorstate()

	while True:
		state, changed = doorstate()
		#print("Checking door state: {} (was {})".format(state, laststate))

		if state != laststate:
			print("Door status changed!")
			changetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(lastchanged))
			t = time.mktime(time.localtime()) - time.mktime(time.localtime(lastchanged))
			changeduration = "{} Tagen {} Stunden, {} Minuten und {} Sekunden".format(
				int(t // (24 * 3600)),
				int(t // 3600),
				int(t % 3600 // 60),
				int(t % 60)
			)

			if state:
				irc("NOTICE", "#hackerspace", ":nordlab ist offen (war seit dem {} für {} geschlossen)\r\n".format(changetime, changeduration))
			else:
				irc("NOTICE", "#hackerspace", ":nordlab ist geschlossen (war seit dem {} für {} geöffnet)\r\n".format(changetime, changeduration))

			laststate = state
			lastchanged = changed

		time.sleep(interval)

def loggedin(irc, *args):
	irc("JOIN", "#hackerspace")

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
