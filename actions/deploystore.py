import webapp2
import json
import logging
import math
import time

logging.basicConfig(filename='deploystore.log', level=logging.INFO)

# built-in libraries
from datetime import datetime, date

# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache

# config
from config			import config

# models
from models.Storeitem 	import Storeitem

class deploystore(webapp2.RequestHandler):
	
	error = ''
	respn = ''
	debug = ''
	
	def reset(self):
		self.error = ''
		self.respn = ''
		self.debug = ''
	
	def required(self, par_name):
		if self.error == "": 
			if self.request.get(par_name):
				return self.request.get(par_name)
			else: 
				self.error = par_name + " is a required parameter."
		return "undefined"
	
	
	def get(self):
	
		self.reset()
		
		# validate
		passwd	= self.required('passwd')
		version = self.required('version')
		data	= self.required('data')
		
		
		if self.error == '' and passwd != config.testing['passwd']:
			self.error = 'passwd is incorrect.'
		
		start_time = time.time()
		
		if self.error == '':
			_memcache = False			
			storeitem = memcache.get(config.db['storeitem_name']+'.'+version)
			if storeitem is None:
				storeitems = Storeitem.all().filter('version =', version).ancestor(db.Key.from_path('Storeitem', config.db['storeitem_name'])).fetch(1);
				if len(storeitems)>=1:
					storeitem = storeitems[0]
				else:
					storeitem = Storeitem(parent=db.Key.from_path('Storeitem', config.db['storeitem_name']))
			else:
				_memcache = True
				
			if storeitem is not None:
				
				storeitem.version = version
				storeitem.data = data
				if storeitem.put():
					self.respn = '"Deploy successfully!"'
				else:
					self.error = 'Deploy failed - couldn\'t update database!'
			
				if _memcache==False:
					if not memcache.add(config.db['storeitem_name']+'.'+version, storeitem, config.memcache['holdtime']):
						logging.warning('deploystore - Memcache set failed')
						
		# return
		time_taken =  time.time() - start_time;
		self.debug += '('+str(time_taken)+')'
		self.response.headers['Content-Type'] = 'text/html'
		if self.respn == '': 
			self.respn = '""'
		else:
			if (self.respn[0] != '{' or self.respn[len(self.respn)-1] != '}') and (self.respn[0] != '[' or self.respn[len(self.respn)-1] != ']') and (self.respn[0] != '"' or self.respn[len(self.respn)-1] != '"'):
				self.respn = '"'+self.respn+'"' 
		if self.request.get('debug'):
			self.response.write('{"response":'+self.respn+',"error":"'+self.error+'", "debug":"'+self.debug+'"}')
		else:
			self.response.write('{"response":'+self.respn+',"error":"'+self.error+'"}')
		
		
	def post(self):
		self.get()