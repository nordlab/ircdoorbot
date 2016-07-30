#!/usr/bin/env python3

import socket
import sys
import queue
import select

"""
Module for sending and receiving IRC messages.

This module is suited for easy understandable (primitive) understand bots.

Currently it implements a single class:
IRC

WARNING: This module does NOT implement the full IRC specifications and
could cause trouble for IRC operators and could be unreliable.
"""

class InvalidParameterCountError(Exception):
	pass

class InvalidCommandError(Exception):
	pass

class MessageTooLongError(Exception):
	pass

class IRC:
	"""
	Implements some simple methods for a primitive IRC session.
	"""

	s = None
	"""Socket used for the connection."""

	buf = ""
	"""Buffer for storing receipt data."""

	commands = [
		"NICK",
		"USER",
		"JOIN",
		"NOTICE",
		"QUIT",
		"PONG"
	]
	"""Supported commands for sending."""

	outQueue = queue.Queue()
	"""Messages for sending will be queued."""

	def __call__(self, *args):
		"""
		To quickly send a message to the server the object can be called
		instead of IRC.send(). The arguments will be passed to IRC.format()
		to properly check and format the message.

		Positional arguments:
		args -- arbitrary arguments from which a message will be formed

		The method does not return something.
		"""

		self.send(self.format(*args))

	def connect(self, host, port=6667):
		"""
		Create a socket and connect it to the host and specified port.

		The socket is stored in the class attribute IRC.s.

		Positional arguments:
		host -- the host as string to connect to

		Keyword arguments:
		port -- the port of the IRC server to connect to (default 6667)

		The method does not return something.
		"""

		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		self.s.connect((host, port))

	def disconnect(self):
		"""
		Disconnect from the IRC server by directly sending the QUIT command.

		The QUIT command is sent directly instead of being queued in
		IRC.outQueue.

		Afterwards the socket connection is closed.

		The method does not return something.
		"""

		self.send("QUIT", True)

		if self.s is not None:
			self.s.close()

	def format(self, command, *params):
		"""
		Helper method to format a message which will be sent to the server.

		The method checks if the command is supported by this class, the
		maximum length defined in the RFC and makes sure the command and its
		parameters are seperated by a single space.

		Positional arguments:
		command -- the command as string
		params -- additional parameters seperated by a
		          single space which might be necessary for the command
		          (optional)

		The method does not return something.
		"""

		if command.upper() not in self.commands:
			raise InvalidCommandError("Unknown command")

		# See RFC 2812 2.3 Messages (2nd paragraph)
		if len(params) > 15:
			raise InvalidParameterCountError(
				"Too much parameters (only 15 allowed)"
			)

		m = "{} {}\r\n".format(command, " ".join(str(x) for x in params))

		if len(m) > 512:
			raise MessageTooLongError("Message exceeds 512 characters")

		return m

	def send(self, m, direct=False):
		"""
		Send a UTF-8 encoded string to the IRC server.

		Positional arguments:
		m -- The message to send as string

		Keyword arguments:
		direct -- whether to send directly via socket or enque the message
		          (default False)

		The method does not return something.
		"""

		if direct:
			self.s.send(bytes(m, "utf-8"))
		else:
			self.outQueue.put_nowait(m)

	def receiveLines(self):
		r"""
		Receive and decode UTF-8 data from the server and append it to IRC.buf.

		The message is split on each line (seperated by "\r\n").

		Returns a generator for iterating over the lines in the receiver buffer
		IRC.buf.
		"""

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
		"""
		Handle IRC messages by parsing them and reacting to the commands.

		Positional arguments:
		m -- the receipt message which will be parsed.

		The method does not return something.
		"""

		line = m.split(" ")

		if line[0] == "PING":
			self("PONG", line[1])
		elif line[1] == "001":
			irc("JOIN", "#hackerspace")

	def start(self):
		"""
		Start the main loop which continuously checks if the socket is ready to
		receive and read the available data via IRC.receiveLines() which is
		then handled by IRC.handle(). Messages for sending are stored in the
		queue IRC.outQueue which is polled for a single message if the socket
		is ready to send.

		The method does not return something.
		"""

		while True:
			inputReady, outputReady, exceptReady = select.select(
				[self.s],
				[],
				[]
			)

			# Ready for receiving
			if len(inputReady) > 0 and inputReady[0] == self.s:
				# Read lines until input buffer is empty
				for line in irc.receiveLines():
					if len(line) > 0:
						print(line)

					self.handle(line)

			# Only send if there is something to send
			if not self.outQueue.empty():
				m = self.outQueue.get_nowait()

				print("Sending '{}'".format(m.rstrip("\r\n")))
				self.s.send(bytes(m, "utf-8"))
				self.outQueue.task_done()

if __name__ == "__main__":
	try:
		irc = IRC()

		irc.connect("irc.lugfl.de")
		irc("NICK", "testbot")
		irc("USER", "testbot", "irc.lugfl.de", "*", ":Test Bot")

		irc.start()
	finally:
		print("Disconnecting...")
		irc.disconnect()
