# built-in libraries
import json

# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache

# config
from config				import config

class Item(db.Model):
	uuid 			= db.StringProperty()
	itid			= db.StringProperty()
	inid 			= db.StringProperty(indexed=False)
	status			= db.StringProperty()
	timestamp		= db.FloatProperty(indexed=False)
	created			= db.DateTimeProperty(auto_now_add=True)
	
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