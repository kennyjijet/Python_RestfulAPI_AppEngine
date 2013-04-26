import webapp2
import json
import logging
logging.basicConfig(filename='saveplayer.log', level=logging.INFO)
import time

# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache

# config
from config			import config

# models
from models.Player import Player

# include
from controllers.Core 	import Core
from helpers.utils		import Utils

class saveplayer(webapp2.RequestHandler):
	
	sinfo = ''
	respn = ''
	error = ''
	debug = ''
	
	def get(self):
		Utils.reset(self)
		
		# validate
		passwd	= Utils.required(self, 'passwd')
		uuid	= Utils.geneuuid(self, 'uuid')
		token	= self.request.get('token')
		name	= Utils.required(self, 'name')
		photo	= Utils.required(self, 'photo')
		platinum= 10
		gold	= 5000
		
		if self.error == '' and passwd != config.testing['passwd']:
			self.error = 'passwd is incorrect.'
		start_time = time.time()
		
		if self.error == '':
			player = Core.getplayer(self, uuid)
			if player is None:
				player = Player(parent=db.Key.from_path('Player', config.db['playerdb_name']))
				player.uuid = uuid # = Utils.geneuuid(self, 'random')
				player.state  = '{'
				player.state += '"token":"'		+token+		'",'
				player.state += '"name":"'		+name+			'",'
				player.state += '"photo":"'		+photo+			'",'
				player.state += '"platinum":'	+str(platinum)+	','
				player.state += '"gold":'		+str(gold)+		''
				player.state += '}'
			else:
				player_obj = json.loads(player.state)
				if token:
					player_obj['token'] = token
				player_obj['name'] = name
				player_obj['photo'] = photo
				player.state = json.dumps(player_obj)
				
			if player.put():
				self.error = ''
				self.respn	= '{'
				self.respn += '"uuid":"'	+player.uuid	+'",'
				self.respn += '"state": ' +player.state
				self.respn += '}'
			else:
				self.error = 'unable to insert/update player data.'
		
			memcache.delete(config.db['playerdb_name']+'.'+uuid)
			if not memcache.add(config.db['playerdb_name']+'.'+uuid, player, config.memcache['holdtime']):
				logging.warning('saveplayer - Memcache set failed')
						
		# return
		time_taken =  time.time() - start_time
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))
		

	def post(self):
		self.get()