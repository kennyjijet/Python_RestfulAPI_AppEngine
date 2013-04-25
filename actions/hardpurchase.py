import webapp2
import json
import logging
import math
import time
import base64
import urllib2
import hashlib

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
from models.Record		import Record

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
		
		#################################
		# validation input paramenters
		uuid	= self.required('uuid')
		itemid 	= self.required('itemid')
		receipt = self.required('receipt')
		
		start_time = time.time()
		
		##################################
		# if parameters are ok, check user
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
		
		##################################
		# if user exists, then process hard purchase
		if self.error == '' and player is not None:	
		
			# hash receipt
			m = hashlib.md5()
			m.update(receipt)
			hreceipt = m.hexdigest()
			
			# find record
			record = memcache.get(config.db['recorddb_name']+'.'+hreceipt)
			if record is None:
				records = Record.all().filter('hreceipt =', hreceipt).ancestor(db.Key.from_path('Record', config.db['recorddb_name'])).fetch(1)
				if len(records)>=1:
					record = records[0]
					if record.status == 'rewarded':
						self.error = 'This item has been rewarded to user'
						record = None
				else:
					record = Record(parent=db.Key.from_path('Record', config.db['recorddb_name']))
					record.uuid = uuid
					record.itemid = itemid
					record.hreceipt = hreceipt
					record.status = 'pending'
					if record.put():
						if not memcache.add(config.db['recorddb_name']+'.'+hreceipt, record, config.memcache['holdtime']):
							logging.warning('hardpurchase - Memcache set record failed')
			
			if record is not None:
			
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

						_memcache = False
						storeitem = memcache.get(config.db['storeitem_name']+'.'+config.softstore['version'])
						if storeitem is None:
							storeitems = Storeitem.all().filter('version =', config.softstore['version']).ancestor(db.Key.from_path('Storeitem', config.db['storeitem_name'])).fetch(1)
							if len(storeitems)>=1:
								storeitem = storeitems[0]
							else:
								self.error = 'Store data couldn\'t be retrieved!'
								storeitem = None
						else:
							_memcache = True
							
						if storeitem is not None:
							storeitem_obj = json.loads(storeitem.data)
							item = None
							for i in storeitem_obj:
								logging.info(i['id']+'=='+resultobj['receipt']['product_id'])
								if i['id'] == resultobj['receipt']['product_id']:
									item = i
									break
							if item is not None:
								player_obj = json.loads(player.state)
								player_obj['platinum'] = player_obj['platinum']+item['platinum']
								player.state = json.dumps(player_obj)
								if player.put():
									record.status = 'rewarded'
									if record.put():
										self.respn = '{"uuid":"'+player.uuid+'", "state":'+player.state+'}';
										if not memcache.delete(config.db['recorddb_name']+'.'+hreceipt):
											logging.warning('hardpurchase - Memcache delete record failed')
										if not memcache.delete(config.db['playerdb_name']+'.'+uuid):
											logging.warning('hardpurchase - Memcache delete player failed')
							else:
								self.error = 'Item couldn\'t be found in the current shop\'s version'
							
										
							if _memcache==False:
								if not memcache.add(config.db['storeitem_name']+'.'+config.softstore['version'], storeitem, config.memcache['holdtime']):
									logging.warning('hardpurchase - Memcache set storeitem failed')
					else:
						self.error = 'transaction reciept is invalid'
						record.status = str(resultobj['status'])
						record.put()
					

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