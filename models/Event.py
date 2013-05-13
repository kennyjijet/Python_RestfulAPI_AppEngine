# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache

# config
from config			import config
	
class Event(db.Model):
	version 			= db.StringProperty()
	data 				= db.TextProperty()
	created				= db.DateTimeProperty(auto_now_add=True)
	
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