import webapp2
import json
import logging
logging.basicConfig(filename='getsoftstore.log', level=logging.INFO)
import time

# config
from config				import config
# include
from controllers.Core	import Core
from helpers.utils		import Utils


class getsoftstore(webapp2.RequestHandler):
	
	sinfo = ''
	respn = ''
	error = ''
	debug = ''
	
	def reset(self):
		self.sinfo = ''
		self.respn = ''
		self.error = ''
		self.debug = ''
	
	def get(self):
		self.reset()
			
		# validate
		version =  config.softstore['version']
		if self.request.get('version'):
			version = self.request.get('version')
		uuid	= Utils.required(self, 'uuid')
		start_time = time.time()
			
		if self.error == '':	
			player = Core.getplayer(self, uuid)
		
		if self.error == '' and player is not None:
			storeitem = Core.getstoreitem_as_arr(self, version)
			
		if self.error == '' and storeitem is not None:
			player_obj = json.loads(player.state)
			storeitem_obj = storeitem
			myitems = Core.getitems(self, uuid)
			
			self.respn = '['
			reason = ''
			for item in storeitem_obj:

				add = True
				if item['dependencies'] != '':
					add = False
					reason = 'You need the following items first: ' + item['dependencies'];
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
						reason = 'You\'ve reached the maximum of this item!'
						
				self.respn += '{'
				self.respn += ' "id":"'+item['id']+'",'
				self.respn += ' "type":"'+item['type']+'",'
				self.respn += ' "title":"'+item['title']+'",'
				self.respn += ' "description":"'+item['description']+'",'
				self.respn += ' "dependencies":"'+item['dependencies']+'",'
				self.respn += ' "imgurl":"'+item['imgurl']+'",'
				self.respn += ' "gold":'+str(item['gold'])+','
				self.respn += ' "time":'+str(item['time'])+','
				self.respn += ' "platinum":'+str(item['platinum'])+','
				if add == True:
					self.respn += ' "lock":""'
				else:
					self.respn += ' "lock":"'+reason+'"'
				self.respn += '},'
					
			self.respn = self.respn.rstrip(',') + ']'
				
		# return
		time_taken =  time.time() - start_time;
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))
		
		
	def post(self):
		self.get()