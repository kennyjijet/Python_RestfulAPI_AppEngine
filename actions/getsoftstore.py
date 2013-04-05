import webapp2
import json
import logging
import math
import time

logging.basicConfig(filename='getsoftstore.log', level=logging.INFO)

# built-in libraries
from datetime import datetime, date

# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache

# config
from config			import config

# models
from models.Storeitem 	import Storeitem
from models.Player		import Player

class getsoftstore(webapp2.RequestHandler):
	
	error = ''
	respn = ''
	debug = ''
	
	def reset(self):
		self.error = ''
		self.respn = ''
		self.debug = ''
	
	def required(self, par_name):
		if self.error == "": 
			if self.request.get(par_name):
				return self.request.get(par_name)
			else: 
				self.error = par_name + " is a required parameter."
		return "undefined"
	
	
	def get(self):
	
		self.reset()
		
		# validate
		uuid	= self.required('uuid')
		
		start_time = time.time()
		
		if self.error == '':
			_memcache = False			
			player = memcache.get(config.db['playerdb_name']+'.'+uuid)
			if player is None:
				players = Player.all().filter('uuid =', uuid).ancestor(db.Key.from_path('Player', config.db['playerdb_name'])).fetch(1);
				if len(players)>=1:
					player = players[0]
				else:
					self.error = 'uuid='+uuid+' was not found.'
					player = None
			else:
				_memcache = True
				
			if player is not None:
				if _memcache==False:
					if not memcache.add(config.db['playerdb_name']+'.'+uuid, player, config.memcache['holdtime']):
						logging.warning('getsoftstore - Memcache set player failed')
		
		if self.error == '' and player is not None:
			_memcache = False			
			storeitem = memcache.get(config.db['storeitem_name']+'.'+config.softstore['version'])
			if storeitem is None:
				storeitems = Storeitem.all().filter('version =', config.softstore['version']).ancestor(db.Key.from_path('Storeitem', config.db['storeitem_name'])).fetch(1);
				if len(storeitems)>=1:
					storeitem = storeitems[0]
				else:
					self.error = 'Store data couldn\'t be retrieved!'
					storeitem = None
			else:
				_memcache = True
				
			if storeitem is not None:
				
				player_obj = json.loads(player.state)
				storeitem_obj = json.loads(storeitem.data)
				
				self.respn = '['
				
				for item in storeitem_obj:
				
					add = True
					if item['dependencies'] != '':
						add = False
						depc = 0
						deps = item['dependencies'].replace(' ', '').split(',')
						for dep in deps:
							for myitem in player_obj['inventory']:
								if player_obj['inventory'][myitem]['id'] == dep:
									depc = depc + 1
						if depc >= len(deps):
							add = True
						
					self.respn += '{'
					self.respn += ' "id":"'+item['id']+'",'
					self.respn += ' "type":"'+item['type']+'",'
					self.respn += ' "title":"'+item['title']+'",'
					self.respn += ' "description":"'+item['description']+'",'
					self.respn += ' "dependencies":"'+item['dependencies']+'",'
					self.respn += ' "gold":'+str(item['gold'])+','
					self.respn += ' "time":'+str(item['time'])+','
					self.respn += ' "platinum":'+str(item['platinum'])+','
					if add == True:
						self.respn += ' "unlock":true'
					else:
						self.respn += ' "unlock":false'
					self.respn += '},'
						
				self.respn = self.respn.rstrip(',') + ']'
				
				if _memcache==False:
					if not memcache.add(config.db['storeitem_name']+'.'+config.softstore['version'], storeitem, config.memcache['holdtime']):
						logging.warning('getsoftstore - Memcache set storeitem failed')
						
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