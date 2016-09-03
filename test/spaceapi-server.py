#!/usr/bin/env python3

from socketserver import TCPServer
from http.server import BaseHTTPRequestHandler
from http import HTTPStatus
import http.client
import json
import os
from collections import OrderedDict

# Credits:
# https://gist.github.com/bradmontgomery/2219997
# https://stackoverflow.com/questions/3474045/problems-with-my-basehttpserver
# https://docs.python.org/3.5/library/http.server.html
class RequestHandler(BaseHTTPRequestHandler):
	def _headers(self):
		self.send_response(HTTPStatus.OK)
		self.send_header("Content-Type", "application/javascript; charset=UTF-8")
		self.end_headers()
	
	def _content(self, content=None):
		if content is None:
			with open("status.txt") as f:
				status = f.read().strip() == "opened"

			changetime = int(os.path.getmtime("status.txt"))

			data = OrderedDict({
				"api": "0.13",
				"space": "nordlab e. V.",
				"logo": "http://nordlab-ev.de/img/null.png",
				"url": "http://nordlab-ev.de",
				"location": {
					"address": "nordlab e. V., Offener Kanal Flensburg, St.-Jürgen-Straße 95, 24937 Flensburg",
					"lat": 54.791614,
					"lon": 9.442367
				},
				"contact": {
					"ml": "nordlab@lists.nordlab-ev.de",
					"irc": "irc://irc.lugfl.de:6668/#hackerspace",
					"twitter": "@nordlab",
					"phone": "+49 461 574945880"
				},
				"issue_report_channels": [ "twitter" ],
				"state": {
					"open": status,
					"lastchange": changetime
				},
				"projects": [ "http://freifunk-flensburg.de" ],
				"open": status,
				"icon": {
					"open": "",
					"closed": ""
				}
			})
			content = json.dumps(data).encode("utf-8")

		return content.strip()

	def do_HEAD(self):
		self._headers()

	def do_GET(self):
		self._headers()
		self.wfile.write(self._content())

	def do_POST(self):
		length = int(self.headers.get("Content-Length"))
		data = self.rfile.read(length)
		self._headers()
		self.wfile.write(self._content(data.decode("utf-8")).encode("utf-8"))

if __name__ == "__main__":
	HOST, PORT = "localhost", 8001

	try:
		httpd = TCPServer((HOST, PORT), RequestHandler)

		print("Serving HTTP at port", PORT)
		httpd.serve_forever()
	except KeyboardInterrupt:
		print("Shutting down HTTP server")
		httpd.shutdown()
		httpd.server_close()
		print()
