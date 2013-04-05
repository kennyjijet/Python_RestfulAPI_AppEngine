import webapp2
import json
import logging
import math
import time
import base64
import urllib2

logging.basicConfig(filename='hardpurchase.log', level=logging.INFO)

# built-in libraries
from random 		import randint
from datetime 		import datetime, date

# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache, urlfetch

# config
from config			import config

# models
from models.Storeitem 	import Storeitem
from models.Player		import Player

class hardpurchase(webapp2.RequestHandler):
	
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
		itemid 	= self.required('itemid')
		receipt = self.required('receipt')
		
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
						logging.warning('softpurchase - Memcache set player failed')
		
		if self.error == '' and player is not None:	
			
			if config.apple['sandbox']==True: 
				url = config.apple['verifyingReceiptSandboxURL']
			else:
				url = config.apple['verifyingReceiptURL']
			
			result = urlfetch.fetch(url=url,
                        payload='{"receipt-data":"'+receipt+'"}',
                        method=urlfetch.POST,
                        headers={'Content-Type': 'text/json; charset=utf-8'},
						validate_certificate=False)

			if result.status_code == 200: 
				resultobj = json.loads(result.content)
				if resultobj['status']==0:
					player_obj = json.loads(player.state)
					player_obj['platinum'] = player_obj['platinum']+10
					player.state = json.dumps(player_obj)
					if player.put():
						self.respn = '{"uuid":"'+player.uuid+'", "state":'+player.state+'}';
						if not memcache.delete(config.db['playerdb_name']+'.'+uuid):
							logging.warning('purchasesoftitem - Memcache delete player failed')
	
				else:
					self.error = 'transaction reciept is invalid'


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