import webapp2
import json
import logging
import math
import time
#import socket, ssl

logging.basicConfig(filename='exam.log', level=logging.INFO)

# built-in libraries
from datetime 		import datetime, date

from google.appengine.api import memcache, urlfetch

# config
from config			import config

# include
from helpers.apns	import apns
from helpers.utils	import Utils

class sendnotifications(webapp2.RequestHandler):
	
	sinfo = ''
	respn = ''
	error = ''
	debug = ''
	
	def get(self):
		Utils.reset(self)
	
		# validate
		
		start_time = time.time()

		#apns.add('12345', 'Pingya', 1234.5);
		self.respn = '{"info":"no notification!"}'
		list = apns.get()
		parameter = '[]'
		if(list):
			parameter = json.dumps(list);
			
		result = urlfetch.fetch(url=config.apns['proxyurl'],
				payload='{"data":'+parameter+', "time":'+str(start_time)+',"passwd":"'+config.testing['passwd']+'"}',
				method=urlfetch.POST,
				headers={'Content-Type': 'text/json; charset=utf-8'},
				validate_certificate=False)
		if result.status_code == 200:
			self.respn = result.content
				
		apns.clean()
				
		logging.info(self.respn)
		# return
		time_taken =  time.time() - start_time;
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))	
		
		
	def post(self):
		self.get()