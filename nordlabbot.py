#!/usr/bin/env python3

import socket
import string
import urllib.request
import json
import time
import threading

HOST = "irc.lugfl.de"
PORT = 6667
NICK = "bot"
USER = "bot"
REALNAME = "Test bot"
CHANNEL = "#bottest"
CHECKINTERVAL = 10

def receive(s, buf):
	buf = buf + s.recv(1024).decode("utf-8")
	lines = buf.split("\n")
	# The last line in this list is possibly a half-received line, so it is stored back into the read buffer.
	buf = lines.pop()

	for line in lines:
		line = line[:-1] # Strip "\r" from line end
		line = line.split()

		if line[0] == "PING":
			s.send(bytes("PONG {}\r\n".format(line[1]), "utf-8"))

		"""
		# First word is the user string
		if line[1] == "PRIVMSG":
			sender = ""

			for char in line[0]:
				if char == "!":
					break
				if char != ":":
					sender += char

			size = len(line)
			i = 3
			message = ""

			while i < size:
				message += line[i] + " "
				i += 1

			message.lstrip(":")
			s.send(bytes("PRIVMSG {} {}\r\n".format(sender, message), "utf-8"))
		"""

		print(" ".join(line))

def doorstate():
	spaceApiUri = "http://spaceapi.nordlab-ev.de/"
	result = None

	with urllib.request.urlopen(spaceApiUri) as c:
		result = c.read().decode("utf-8")
	
	spaceApi = json.loads(result)

	return (spaceApi["state"]["open"], spaceApi["state"]["lastchange"])

def checkdoor(s):
	laststate, lastchanged = (None, None)

	while True:
		state, changed = doorstate()
		#print("Checking door state: {} (was {})".format(state, laststate))

		if state != laststate:
			#print("Door status changed!")
			changetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(lastchanged))
			t = time.mktime(time.localtime()) - time.mktime(time.localtime(lastchanged))
			changeduration = "{} Tagen {} Stunden, {} Minuten und {} Sekunden".format(int(t // (24 * 3600)), int(t // 3600), int(t % 3600 // 60), int(t % 60))

			if (state):
				s.send(bytes("NOTICE #hackerspace :nordlab ist offen (war seit dem {} für {} geschlossen)\r\n".format(changetime, changeduration), "utf-8"))
			else:
				s.send(bytes("NOTICE #hackerspace :nordlab ist geschlossen (war seit dem {} für {} geöffnet)\r\n".format(changetime, changeduration), "utf-8"))

			laststate = state
			lastchanged = changed

		time.sleep(CHECKINTERVAL)

readbuffer = ""

s = socket.socket()

s.connect((HOST, PORT))

doorchecker = threading.Thread(target=checkdoor, args=(s,))
doorchecker.daemon = True
#doorchecker.start()

s.sendall(bytes("NICK {}\r\n".format(NICK), "utf-8"))
receive(s, readbuffer)
s.sendall(bytes("USER {} {} * :{}\r\n".format(USER, HOST, REALNAME), "utf-8"))
receive(s, readbuffer)
s.send(bytes("JOIN {}\r\n".format(CHANNEL), "utf-8"))

while True:
	receive(s, readbuffer)
