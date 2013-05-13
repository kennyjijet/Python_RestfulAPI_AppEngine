"""
used by the Grandcentral API to find and return a players items
uses the Core class to get the items from memcache or datastore

if successful returns a JSON packet containing all items, for example :
 
 	result:
 	
The script will fail if no player uuid is supplied and will return an error ?

If the player uuid is invalid then the following


"""


import webapp2
import json
import logging
logging.basicConfig(filename='loadplayer.log', level=logging.INFO)
import time

from google.appengine.api import memcache

# config
from config				import config
# include
from controllers.Core	import Core
from helpers.utils		import Utils


class getmyitems(webapp2.RequestHandler):
	
	sinfo = ''
	respn = ''
	error = ''
	debug = ''
		
	def get(self):
		Utils.reset(self)
		
		#validate
		version =  config.softstore['version']
		if self.request.get('version'):
			version = self.request.get('version')
		uuid 	= Utils.required(self, 'uuid');
		start_time = time.time()

			
		if self.error == '':	
			player = Core.getplayer(self, uuid)
			
		if self.error == '' and player is not None:
			storeitem = Core.getstoreitem_as_obj(self, version)
			items = None
			if storeitem is not None:
				items = Core.getitems(self, uuid)				
			if items is not None:
				change = 0
				self.respn = '{'
				for item in items:
					if storeitem[str(item.itid)]:
					
						save = False
						if item.status == 'pending' and time.time() >= item.timestamp:
							item.status = 'reward'
							item.timestamp = time.time() + storeitem[str(item.itid)]['produce_time']
							save = True
						elif item.status == 'reward':
							item.status = 'rewarded'
							save = True
						
						if storeitem[str(item.itid)]['time'] >= 0:
							if item.status == 'reward' or item.status == 'rewarded':
								if time.time() > item.timestamp:
									item.status = 'produced'
									save = True
															
						self.respn += '"'+item.inid+'":{'
						self.respn += '"itid"		: "'+item.itid+'",'
						self.respn += '"type"		: "'+storeitem[str(item.itid)]['type']+'",'
						self.respn += '"title"		: "'+storeitem[str(item.itid)]['title']+'",'
						self.respn += '"desc"		: "'+storeitem[str(item.itid)]['description']+'",'
						self.respn += '"imgurl"		: "'+storeitem[str(item.itid)]['image_url_sd']+'",'
						self.respn += '"status"		: "'+item.status+'",'
						self.respn += '"timestamp"		: '+str(item.timestamp)
						self.respn += '},'
						
						if save == True:
							item.put()
							
				self.respn = self.respn.rstrip(',') + '}'
				#self.respn = self.respn.rstrip(',') + ']'
				
				if change > 0:
					memcache.delete(config.db['itemdb_name']+'.'+uuid)
					if not memcache.add(config.db['itemdb_name']+'.'+uuid, items, config.memcache['holdtime']):
						logging.warning('Core - Memcache set items failed')
				
		# return
		time_taken =  time.time() - start_time;
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))
		
	def post(self):
		self.get()
