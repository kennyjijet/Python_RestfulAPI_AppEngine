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
from helpers.apns		import apns

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
		itid	= Utils.required(self, 'itid')
		start_time = time.time()
		
		item = None
		player = None
		storeitem = None
		
		if self.error == '':
			player = Core.getplayer(self, uuid)
		
		if self.error == '' and player is not None:		
			storeitem = Core.getstoreitem_as_obj(self, version)

		if storeitem is not None:
			try:
				item = storeitem[str(itid)]
			except KeyError:
				storeitem = None;
				self.error = 'given item id doesn\'t exist!'
		
		if self.error == '' and storeitem is not None:
		
			player_obj = json.loads(player.state)
			storeitem_obj = storeitem
			myitems = Core.getitems(self, uuid)
					
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
					itemobj.inid = Utils.genitemid(self) 
					itemobj.uuid = player.uuid
					itemobj.status =  'pending'
					itemobj.timestamp = time.time()+float(item['time'])
					if itemobj.put():	
						if player_obj['token'] != '': 
							apns.add(player_obj['token'], storeitem[str(itemobj.itid)]['title']+' has been delivered to you!', itemobj.timestamp)
						player.state = json.dumps(player_obj)
						if player.put():
							
							myitems = Core.getspecificitems(self, uuid, item['id'])
							if myitems is not None:
								self.respn = '{'
								for myitem in myitems:
									if storeitem[str(myitem.itid)]:
									
										save = False
										"""
										if myitem.status > 1.0 and time.time() >= myitem.status:
											myitem.status = 1.0
											save = True
										elif myitem.status == 1.0:
											myitem.status = 0.0
											save = True
										"""
										if myitem.status == 'pending' and time.time() >= myitem.timestamp:
											myitem.status = 'reward'
											myitem.timestamp = time.time() + storeitem[str(myitem.itid)]['time'] * 3600 #convert hour to milisecs
											save = True
										elif myitem.status == 'reward':
											myitem.status = 'rewarded'
											save = True
											
										self.respn += '"'+myitem.inid+'":{'
										self.respn += '"itid"		: "'+myitem.itid+'",'
										self.respn += '"type"		: "'+storeitem[str(myitem.itid)]['type']+'",'
										self.respn += '"title"		: "'+storeitem[str(myitem.itid)]['title']+'",'
										self.respn += '"desc"		: "'+storeitem[str(myitem.itid)]['description']+'",'
										self.respn += '"imgurl"		: "'+storeitem[str(myitem.itid)]['image_url_sd']+'",'
										self.respn += '"status"		: "'+myitem.status+'",'
										self.respn += '"timestamp"		: '+str(myitem.timestamp)
										self.respn += '},'
										
										if save == True:
											myitem.put()
											
								self.respn = self.respn.rstrip(',') + '}'
							else:
								self.respn = '{}';
							
							self.respn = '{"uuid":"'+player.uuid+'", "state":'+player.state+', "items":'+self.respn+'}'
							
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