import webapp2
import time
import logging

logging.basicConfig(filename='deploystore.log', level=logging.INFO)

# config
from config			import config

# include
from helpers.utils 		import Utils
from controllers.Core	import Core

class deployevent(webapp2.RequestHandler):
	
	sinfo = ''
	respn = ''
	error = ''
	debug = ''
	
	def get(self):
		Utils.reset(self)
		
		# validate
		passwd	= Utils.required(self, 'passwd')
		version = Utils.required(self, 'version')
		data	= Utils.required(self, 'data')
		
		if self.error == '' and passwd != config.testing['passwd']:
			self.error = 'passwd is incorrect.'
		
		start_time = time.time()
		
		if self.error == '':
			if Core.setevents(self, version, data):
				self.respn = '"Deploy successfully!"'
			else:
				self.error = 'Deploy failed - couldn\'t update database!'
				
		# return
		time_taken =  time.time() - start_time;
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))
		
		
	def post(self):
		self.get()