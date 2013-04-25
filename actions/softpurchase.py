import webapp2
import json
import logging
import math
import time

logging.basicConfig(filename='softpurchase.log', level=logging.INFO)

# built-in libraries
from random 		import randint
from datetime 		import datetime, date

# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache

# config
from config			import config

# models
from models.Storeitem 	import Storeitem
from models.Player		import Player
from models.Item		import Item

class softpurchase(webapp2.RequestHandler):
	
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
	
	def genitemid(self):		
		now = datetime.now()
		return now.strftime('item%S%y%M%m%H%d')+str(randint(1, 100))
	
	
	def get(self):
	
		self.reset()
		
		# validate
		uuid	= self.required('uuid')
		itemid	= self.required('itemid')
		
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
				for item in storeitem_obj:
								
					if item['id'] == itemid:
						
						add = True
						if item['dependencies'] != '':
							add = False
							self.respn = '{"warning":"you\'re not qualified to purchase this item!"}'
							depc = 0
							deps = item['dependencies'].replace(' ', '').split(',')
							for dep in deps:
								for myitem in player_obj['inventory']:
									if player_obj['inventory'][myitem]['id'] == dep:
										depc = depc + 1
							if depc >= len(deps):
								add = True
					
						if add == True and item['maximum'] != '':
							depc = 0
							for myitem in player_obj['inventory']:
								if player_obj['inventory'][myitem]['id'] == item['id']:
									depc = depc + 1
							if int(depc) >= int(item['maximum']):
								add = False
								self.respn = '{"warning":"you\'ve reached maximum of this item!"}'
							
						if add == True:
							if player_obj['gold'] >= item['gold']:
								player_obj['gold'] = player_obj['gold']-item['gold']
								"""
								itemid = self.genitemid()
								player_obj['inventory'][itemid] = {
									'id':item['id'],
									'type':item['type'],
									'title':item['title'],
									'time':int(time.time())+item['time'],
									'platinum':item['platinum'],
									'active':False
								}
								"""
								itemobj = Item(parent=db.Key.from_path('Item', config.db['itemdb_name']))
								itemobj.itemid = item['id']
								itemobj.ownerid = player.uuid
								itemobj.status = 'pending'
								
								if itemobj.put():								
									player.state = json.dumps(player_obj)
									if player.put():
										self.respn = '{"uuid":"'+player.uuid+'", "state":'+player.state+'}';
										if not memcache.delete(config.db['playerdb_name']+'.'+uuid):
											logging.warning('purchasesoftitem - Memcache set player failed')
							else:
								self.respn = '{"warning":"not enough gold!"}'

				if _memcache==False:
					if not memcache.add(config.db['storeitem_name']+'.'+config.softstore['version'], storeitem, config.memcache['holdtime']):
						logging.warning('purchasesoftitem - Memcache set storeitem failed')
			
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