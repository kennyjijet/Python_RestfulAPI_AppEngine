import webapp2
import json
import logging
logging.basicConfig(filename='softpurchase.log', level=logging.INFO)
import time

# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache

# config
from config				import config
# models
from models.Item		import Item

# include
from controllers.Core 	import Core
from helpers.utils		import Utils

class softpurchase(webapp2.RequestHandler):
	
	sinfo = ''
	respn = ''
	error = ''
	debug = ''
	
	def get(self):
		Utils.reset(self)
			
		# validate
		version =  config.softstore['version']
		if self.request.get('version'):
			version = self.request.get('version')
		uuid	= Utils.required(self, 'uuid')
		itemid	= Utils.required(self, 'itemid')
		start_time = time.time()
		
		item = None
		
		if self.error == '':
			player = Core.getplayer(self, uuid)
		
		if self.error == '' and player is not None:		
			storeitem = Core.getstoreitem_as_obj(self, version)

		if storeitem is not None:
			try:
				item = storeitem[str(itemid)]
			except KeyError:
				storeitem = None;
				self.error = 'given item id doesn\'t exist!'
		
		if self.error == '' and storeitem is not None:
		
			player_obj = json.loads(player.state)
			storeitem_obj = storeitem
			myitems = Core.getitems(self, uuid)
			
			#for item in storeitem:
				#if item['id'] == itemid:
					
			add = True
			if item['dependencies'] != '':
				add = False
				self.respn = '{"warning":"you\'re not qualified to purchase this item!"}'
				depc = 0
				deps = item['dependencies'].replace(' ', '').split(',')
				for dep in deps:
					for myitem in myitems:
						if myitem.itid == dep:
							depc = depc + 1
				if depc >= len(deps):
					add = True
		
			if add == True and item['maximum'] != '':
				depc = 0
				for myitem in myitems:
					if myitem.itid == item['id']:
						depc = depc + 1
				if int(depc) >= int(item['maximum']):
					add = False
					self.respn = '{"warning":"you\'ve reached maximum of this item!"}'
				
			if add == True:
				if player_obj['gold'] >= item['gold']:
					player_obj['gold'] = player_obj['gold']-item['gold']
					itemobj = Item(parent=db.Key.from_path('Item', config.db['itemdb_name']))
					itemobj.itid = item['id']
					itemobj.uuid = player.uuid
					itemobj.status = time.time()+float(item['time']) #'pending'
					if itemobj.put():								
						player.state = json.dumps(player_obj)
						if player.put():
							self.respn = '{"uuid":"'+player.uuid+'", "state":'+player.state+'}';
							memcache.delete(config.db['itemdb_name']+'.'+uuid)
							memcache.delete(config.db['playerdb_name']+'.'+uuid)
							if not memcache.add(config.db['playerdb_name']+'.'+uuid, player, config.memcache['holdtime']):
								logging.warning('purchasesoftitem - Memcache set player failed')
				else:
					self.respn = '{"warning":"not enough gold!"}'

		# return
		time_taken =  time.time() - start_time;
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))
		

	def post(self):
		self.get()