import webapp2
import json
import logging
logging.basicConfig(filename='loadplayer.log', level=logging.INFO)
import time

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
			storeitem = Core.getstoreitem_as_obj(self, version)
			if storeitem is not None:
				items = Core.getitems(self, uuid)
				if items is not None:
					self.respn = '['
					for item in items:
						if storeitem[str(item.itid)]:
							self.respn += '{'
							#self.respn += '"uuid"		: "'+item.uuid+'",'
							self.respn += '"itid"		: "'+item.itid+'",'
							self.respn += '"title"		: "'+storeitem[str(item.itid)]['title']+'",'
							self.respn += '"description": "'+storeitem[str(item.itid)]['description']+'",'
							self.respn += '"imgurl"		: "'+storeitem[str(item.itid)]['imgurl']+'",'
							self.respn += '"status"		: "'+str(item.status)+'"'
							self.respn += '},'
					self.respn = self.respn.rstrip(',') + ']'
						
		# return
		time_taken =  time.time() - start_time;
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))
		
	def post(self):
		self.get()