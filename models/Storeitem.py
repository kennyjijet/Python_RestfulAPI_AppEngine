# built-in libraries
import json

# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache

# config
from config				import config
	
class Storeitem(db.Model):
	version 			= db.StringProperty()
	data 				= db.TextProperty()
	created				= db.DateTimeProperty(auto_now_add=True)
	
	@staticmethod
	def getstoreitem(self, version=str(config.server['apiVersion'])):
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
	def getstoreitem_as_arr(self, version=str(config.server['apiVersion'])):
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
	def getstoreitem_as_obj(self, version=str(config.server['apiVersion'])):
		storeitem = memcache.get(config.db['storeitem_name']+'_as_obj.'+version)
		if storeitem is None:
			storeitems = Storeitem.all().filter('version =', str(float(version))).ancestor(db.Key.from_path('Storeitem', config.db['storeitem_name'])).fetch(1);
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