import webapp2
import json
import logging
import time

logging.basicConfig(filename='exam.log', level=logging.INFO)

# config
from config			import config

# include
from helpers.utils 		import Utils
from controllers.Core 	import Core

class event(webapp2.RequestHandler):
	
	sinfo = ''
	respn = ''
	error = ''
	debug = ''
	
	def get(self):
		Utils.reset(self)
		
		# validate
		passwd = Utils.required(self, 'passwd')
		version = Utils.required(self, 'version')
		evid = Utils.required(self, 'evid')
		#prms = Utils.required(self, 'prms')

		if self.error == '' and passwd != config.testing['passwd']:
			self.error = 'passwd is incorrect.'
			
		start_time = time.time()
		
		if self.error == '':
			events = Core.getevents_as_obj(self, version)
			event = None
			if events is not None:
				try:
					event = events[evid]
				except KeyError:
					self.error = evid + ' does not exist!'
					event = None
			if event is not None:
				self.respn = 'Behaviour is ' + events[evid]['behaviour'];
	
		# return
		time_taken =  time.time() - start_time;
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))
		
		
	def post(self):
		self.get()