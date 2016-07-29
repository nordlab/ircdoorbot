#!/usr/bin/env python3

import socket
from contextlib import contextmanager
import sys

class InvalidParameterCountError(Exception):
	pass

class InvalidCommandError(Exception):
	pass

class MessageTooLongError(Exception):
	pass

class IRC:
	"""
	Socket used for the connection
	"""
	s = None
	"""
	Buffer for storing receipt data
	"""
	buf = ""
	"""
	Supported commands
	"""
	commands = [
		"NICK",
		"USER",
		"JOIN",
		"NOTICE",
		"QUIT",
		"PONG"
	]

	def __call__(self, *args):
		self.send(self.message(*args))

	def connect(self, host, port=6667):
		self.s = socket.socket()

		#self.s.settimeout(10)
		self.s.connect((host, port))

	def disconnect(self):
		if self.s is not None:
			self.s.close()

	def message(self, command, *params):
		if command.upper() not in self.commands:
			raise InvalidCommandError("Unknown command")

		# See RFC 2812 2.3 Messages (2nd paragraph)
		if len(params) > 15:
			raise InvalidParameterCountError("Too much parameters (only 15 allowed)")

		m = "{} {}\r\n".format(command, " ".join(str(x) for x in params))

		if len(m) > 512:
			raise MessageTooLongError("Message exceeds 512 characters")

		return m

	def send(self, m):
		if self.s is None:
			raise ConnectionError("There was a connection error")

		self.s.send(bytes(m, "utf-8"))

	def receiveLines(self):
		if self.s is None:
			raise ConnectionError("There was a connection error")

		if "\r\n" not in self.buf:
			# Read 1024 bytes from socket try to decode it as UTF-8
			# and append it to buffer.
			# It gets appended because there might be incomplete data
			# from a previous read.
			self.buf = self.buf + self.s.recv(1024).decode("utf-8")

		lines = self.buf.split("\r\n", 1)
		line = lines[0]

		if len(lines) > 1:
			self.buf = lines[1]

		yield line

	def handle(self, m):
		line = m.split(" ")

		if line[0] == "PING":
			self("PONG", line[1:])

if __name__ == "__main__":
	try:
		irc = IRC()

		irc.connect("irc.lugfl.de")
		irc("NICK", "testbot")
		irc("USER", "testbot", "irc.lugfl.de", "*", ":Test Bot")

		while True:
			for line in irc.receiveLines():
					print(line, end="")
					irc.handle(line)

		#print(next(irc.receiveLine()))
		#print(next(irc.receiveLine()))
		#print(next(irc.receiveLine()))
		#print(next(irc.receiveLine()))
	finally:
		print("Disconnecting...")
		irc.disconnect()
