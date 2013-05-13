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
	def getproduceditems(self, uuid):
		items = memcache.get(config.db['itemdb_name']+'_produced.'+uuid)
		if items is None:
			items = Item.all().filter('uuid =', uuid).filter('status =', 'produced').ancestor(db.Key.from_path('Item', config.db['itemdb_name']));
			if not memcache.add(config.db['itemdb_name']+'_produced.'+uuid, items, config.memcache['holdtime']):
				logging.warning('Core - Memcache set produced items failed')
		return items
		
	@staticmethod
	def getspecificinidproduceditem(self, uuid, inid):
		items = Core.getproduceditems(self, uuid)
		item = None
		for _item in items:
			if _item.inid == inid:
				item = _item
				break
		
		
		#if item is not None:
		
		return item
			
		
	@staticmethod
	def setevents(self, version, data):
		events = memcache.get(config.db['eventdb_name']+'.'+version)
		if events is None:
			_events = Event.all().filter('version =', version).ancestor(db.Key.from_path('Event', config.db['eventdb_name'])).fetch(1)
			if len(_events) >= 1:
				events = _events[0]
			else:
				events = Event(parent=db.Key.from_path('Event', config.db['eventdb_name']))
		events.version = version
		events.data = data
		if events.put():
			memcache.delete(config.db['eventdb_name']+'.'+version)
			if not memcache.add(config.db['eventdb_name']+'.'+version, events, config.memcache['longtime']):
				logging.warning('Core - Memcache set events failed')
			return True
		return False
		
	@staticmethod
	def getevents_as_obj(self, version=str(config.server['apiVersion'])):
		events = memcache.get(config.db['eventdb_name']+'_as_obj.'+version)
		if events is None:
			events = Event.all().filter('version =', version).ancestor(db.Key.from_path('Event', config.db['eventdb_name'])).fetch(1)
			if len(events) >= 1:
				events = json.loads(events[0].data)
				if not memcache.add(config.db['eventdb_name']+'_as_obj.'+version, events, config.memcache['longtime']):
					logging.warning('Core - Memcache set events failed')
			else:
				self.error = 'Event couldn\'t be retrieved!'
				events = None
		return events
		
		