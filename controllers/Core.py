import json
import logging
logging.basicConfig(filename='core.log', level=logging.INFO)

# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache

# config
from config			import config

# models
from models.Player		import Player
from models.Item		import Item
from models.Storeitem	import Storeitem
from models.Event		import Event

class Core(object):
	
	@staticmethod
	def getplayer(self, uuid): 
		player = memcache.get(config.db['playerdb_name']+'.'+uuid)
		if player is None:
			players = Player.all().filter('uuid =', uuid).ancestor(db.Key.from_path('Player', config.db['playerdb_name'])).fetch(1);
			if len(players)>=1:
				player = players[0]
				if not memcache.add(config.db['playerdb_name']+'.'+uuid, player, config.memcache['holdtime']):
					logging.warning('Core - Memcache set player failed')
			else:
				self.error = 'uuid='+uuid+' was not found.'
				player = None
		return player
		
	@staticmethod
	def getstoreitem(self, version):
		storeitem = memcache.get(config.db['storeitem_name']+'.'+version)
		if storeitem is None:
			storeitems = Storeitem.all().filter('version =', version).ancestor(db.Key.from_path('Storeitem', config.db['storeitem_name'])).fetch(1);
			if len(storeitems)>=1:
				storeitem = json.loads(storeitems[0])
				if not memcache.add(config.db['storeitem_name']+'.'+version, storeitem, config.memcache['longtime']):
					logging.warning('Core - Memcache set storeitem failed')
			else:
				self.error = 'Store data couldn\'t be retrieved!'
				storeitem = None
		return storeitem
		
	@staticmethod
	def getstoreitem_as_arr(self, version):
		storeitem = memcache.get(config.db['storeitem_name']+'_as_arr.'+version)
		if storeitem is None:
			storeitems = Storeitem.all().filter('version =', version).ancestor(db.Key.from_path('Storeitem', config.db['storeitem_name'])).fetch(1);
			if len(storeitems)>=1:
				storeitem = json.loads(storeitems[0].data)	
				if not memcache.add(config.db['storeitem_name']+'_as_arr.'+version, storeitem, config.memcache['longtime']):
					logging.warning('Core - Memcache set storeitem failed')
			else:
				self.error = 'Store data couldn\'t be retrieved!'
				storeitem = None
		return storeitem
		
	@staticmethod
	def getstoreitem_as_obj(self, version):
		storeitem = memcache.get(config.db['storeitem_name']+'_as_obj.'+version)
		if storeitem is None:
			storeitems = Storeitem.all().filter('version =', version).ancestor(db.Key.from_path('Storeitem', config.db['storeitem_name'])).fetch(1);
			if len(storeitems)>=1:
				_storeitem = json.loads(storeitems[0].data)	
				storeitem = {}
				for item in _storeitem:
					storeitem[item['id']] = item
				if not memcache.add(config.db['storeitem_name']+'_as_obj.'+version, storeitem, config.memcache['longtime']):
					logging.warning('Core - Memcache set storeitem failed')
			else:
				self.error = 'Store data couldn\'t be retrieved!'
				storeitem = None
		return storeitem
		
	@staticmethod
	def getitems(self, uuid):
		items = memcache.get(config.db['itemdb_name']+'.'+uuid)
		if items is None:
			items = Item.all().filter('uuid =', uuid).ancestor(db.Key.from_path('Item', config.db['itemdb_name']))
			if not memcache.add(config.db['itemdb_name']+'.'+uuid, items, config.memcache['holdtime']):
				logging.warning('Core - Memcache set items failed')
		return items
		
	@staticmethod
	def getspecificitems(self, uuid, itid):
		items = memcache.get(config.db['itemdb_name']+'.'+itid+'.'+uuid)
		if items is None:
			items = Item.all().filter('uuid =', uuid).filter('itid =', itid).ancestor(db.Key.from_path('Item', config.db['itemdb_name']));
			if not memcache.add(config.db['itemdb_name']+'.'+itid+'.'+uuid, items, config.memcache['holdtime']):
				logging.warning('Core - Memcache set specific item failed')
		return items
		
	@staticmethod
	def setevents(self, version, data):
		events = memcache.get(config.db['eventdb_name']+'.'+version)
		if events is None:
			events = Storeitem(parent=db.Key.from_path('Event', config.db['eventdb_name']))
		events.version = version
		events.data = data
		if events.put():
			memcache.delete(config.db['eventdb_name']+'.'+version)
			if not memcache.add(config.db['eventdb_name']+'.'+version, events, config.memcache['longtime']):
				logging.warning('Core - Memcache set events failed')
			return True
		return False
		
	@staticmethod
	def getevents(self, version):
		events = memcache.get(config.db['eventdb_name']+'.'+version)
		if events is None:
			events = Event.all().filter('version =', version).ancestor(db.Key.from_path('Event', config.db['eventdb_name']))
			if not memcache.add(config.db['eventdb_name']+'.'+version, events, config.memcache['longtime']):
				logging.warning('Core - Memcache set events failed')
		else:
			self.error = 'Event couldn\'t be retrieved!'
			events = None
		return events
		
		