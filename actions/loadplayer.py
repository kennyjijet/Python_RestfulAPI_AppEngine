import webapp2
import json
import logging
import time

logging.basicConfig(filename='loadplayer.log', level=logging.INFO)

# built-in libraries
from random 		import randint
from datetime		import datetime

# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache

# config
from config			import config

# models
from models.Player import Player

class loadplayer(webapp2.RequestHandler):
	
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
		
		#validate
		#passwd	= self.required('passwd')
		uuid 	= self.required('uuid');
		
		#if self.error == '' and passwd != config.testing['passwd']:
		#	self.error = 'passwd is incorrect.'
			
		start_time = time.time()
			
		if self.error == '':
			_memcache = False			
			player = memcache.get(config.db['playerdb_name']+'.'+uuid)
			if player is None:
				players = Player.all().filter('uuid =', uuid).ancestor(db.Key.from_path('Player', config.db['playerdb_name'])).fetch(1);
				if len(players)>=1:
					player = players[0]
				else:
					self.error = 'player data for '+uuid+' was not found.'
					player = None
			else:
				_memcache = True
				
			if player is not None:
				
				self.respn	= '{'
				self.respn += '"uuid"		: "'+player.uuid+'",'
				if player.state[0] != '{' or player.state[len(player.state)-1] != '}': 
					player.state = '"'+player.state+'"' 
				self.respn += '"state"		: '+player.state
				self.respn += '}'
			
				if _memcache==False:
					if not memcache.add(config.db['playerdb_name']+'.'+uuid, player, config.memcache['holdtime']):
						logging.warning('loadplayer - Memcache set failed')
						
		# return
		time_taken =  time.time() - start_time;
		self.debug += '('+str(time_taken)+')'
		self.response.headers['Content-Type'] = 'text/html'
		if self.respn == '': self.respn = '""'
		if self.request.get('debug'):
			self.response.write('{"response":'+self.respn+',"error":"'+self.error+'", "debug":"'+self.debug+'"}')
		else:
			self.response.write('{"response":'+self.respn+',"error":"'+self.error+'"}')
		
	def post(self):
		self.get()