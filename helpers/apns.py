# google's library
from google.appengine.api import memcache

# config
from config				import config
	
class apns:
	
	@staticmethod
	def add(token, msg, time):
		list = memcache.get('apns_list')
		if list is None:
			list = []		
		data = {
			"token":token,
			"msg":msg,
			"time":time
		}
		list.append(data)
		memcache.delete('apns_list')
		memcache.add('apns_list', list, config.memcache['longtime']);
		
	@staticmethod
	def get():
		return memcache.get('apns_list')

	@staticmethod
	def clean():
		memcache.delete('apns_list')
	
	 