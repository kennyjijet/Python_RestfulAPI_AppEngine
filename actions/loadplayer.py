import webapp2
import json
import logging
logging.basicConfig(filename='loadplayer.log', level=logging.INFO)
import time

# config
from config				import config
# include
from controllers.Core	import Core
from helpers.utils		import Utils

class loadplayer(webapp2.RequestHandler):
	
	sinfo = ''
	respn = ''
	error = ''
	debug = ''
		
	def get(self):
		Utils.reset(self)
		
		#validate
		uuid 	= Utils.required(self, 'uuid');
		start_time = time.time()
			
		if self.error == '':		
			player = Core.getplayer(self, uuid)
			if player is not None:
				Utils.compose_player(self, player)
						
		# return
		time_taken =  time.time() - start_time;
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))
		
		
	def post(self):
		self.get()