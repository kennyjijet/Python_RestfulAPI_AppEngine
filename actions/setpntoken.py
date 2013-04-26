import webapp2
import json
import logging
logging.basicConfig(filename='setpntoken.log', level=logging.INFO)
import time

from google.appengine.api import memcache

# config
from config			import config

# include
from controllers.Core 	import Core
from helpers.utils		import Utils

class setpntoken(webapp2.RequestHandler):
	
	sinfo = ''
	respn = ''
	error = ''
	debug = ''
	
	def get(self):
		Utils.reset(self)
		
		# validate
		passwd	= Utils.required(self, 'passwd')
		uuid	= Utils.required(self, 'uuid')
		token	= Utils.required(self, 'token')
		if self.error == '' and passwd != config.testing['passwd']:
			self.error = 'passwd is incorrect.'
		start_time = time.time()
		
		if self.error == '':
			player = Core.getplayer(self, uuid)
			
			if player is not None:
				player_obj = json.loads(player.state)
				player_obj['token'] = token
				player.state = json.dumps(player_obj)
				if player.put():
					self.respn	= '{'
					self.respn += '"uuid":"'	+player.uuid	+'",'
					self.respn += '"state": ' 	+player.state
					self.respn += '}'
					memcache.delete(config.db['playerdb_name']+'.'+uuid)
					if not memcache.add(config.db['playerdb_name']+'.'+uuid, player, config.memcache['holdtime']):
						logging.warning('saveplayer - Memcache set player failed')
				else:
					self.error = 'unable to update player data (token).'
	
		# return
		time_taken =  time.time() - start_time;
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))
		
		
	def post(self):
		self.get()