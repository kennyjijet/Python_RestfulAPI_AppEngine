import webapp2
import json
import logging
import math
import time
#import socket, ssl

logging.basicConfig(filename='exam.log', level=logging.INFO)

# built-in libraries
from datetime 		import datetime, date

# config
from config			import config

class exam(webapp2.RequestHandler):
	
	error = ''
	respn = ''
	debug = ''
	
	def reset(self):
		self.error = ''
		self.respn = ''
		self.debug = ''
	
	def get(self):
	
		self.reset()
		
		# validate
		
		start_time = time.time()
		
		self.respn = "OKss"
		"""
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		ssl_sock = ssl.wrap_socket(sock, server_side=False, keyfile='certs/GamepunksShopKey.pem', certfile='certs/GamepunksShopCert.pem', cert_reqs=ssl.CERT_REQUIRED, ssl_version=ssl.PROTOCOL_TLSv1, ca_certs='/etc/ca-certificates.crt')
		#ssl_sock.connect(('gateway.sandbox.push.apple.com', 2195))
		
		#ssl_sock.write()
		
		#ssl_sock.close();
		"""
		
		# return
		time_taken =  time.time() - start_time;
		self.debug += '('+str(time_taken)+')'
		self.response.headers['Content-Type'] = 'text/html'
		if self.respn == '': 
			self.respn = '""'
		else:
			if (self.respn[0] != '{' or self.respn[len(self.respn)-1] != '}') and (self.respn[0] != '[' or self.respn[len(self.respn)-1] != ']') and (self.respn[0] != '"' or self.respn[len(self.respn)-1] != '"'):
				self.respn = '"'+self.respn+'"' 
		if self.request.get('debug'):
			self.response.write('{"response":'+self.respn+',"error":"'+self.error+'", "debug":"'+self.debug+'"}')
		else:
			self.response.write('{"response":'+self.respn+',"error":"'+self.error+'"}')
		
		
	def post(self):
		self.get()