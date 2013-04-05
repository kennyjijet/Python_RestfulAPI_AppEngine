import webapp2
import json
import logging
import math
import time

logging.basicConfig(filename='loadreplay.log', level=logging.INFO)

from datetime 		import datetime, date, timedelta

# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache

# config
from config			import config

# models
from models.Player 	import Player
from models.Score 	import Score

class loadreplay(webapp2.RequestHandler):
	
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
		#passwd	= self.required('passwd')
		track 	= self.required('track')
					
		#if self.error == '' and passwd != config.testing['passwd']:
		#	self.error = 'passwd is incorrect.'
		
		start_time = time.time()
		
		if self.error == "":
			_memcache = False
			scores = memcache.get(config.db['scoredb_name']+'.'+track)
			if scores is None:
				scores = Score.all().filter('type =', track)
				scores = scores.filter('created_dwmy = ', '0-'+str(int(math.ceil(date.today().day / 7)))+'-'+str(date.today().month)+'-'+str(date.today().year))
				scores = scores.ancestor(db.Key.from_path('Score', config.db['scoredb_name'])).fetch(3);
			else:
				_memcache = True
			
			if scores is not None:
				self.respn = '['
				for score in scores:
					self.respn += '{'
					self.respn += '"uuid":"'	+score.uuid+	'",'
					self.respn += '"track":"'	+score.type+	'",'
					self.respn += '"score":"'	+str(score.point)+'",'
					self.respn += score.data.lstrip('{')
					self.respn += ','
					
				self.respn = self.respn.rstrip(',') + ']'
				
				if _memcache==False:
					if not memcache.add(config.db['scoredb_name']+'.'+track, scores, config.memcache['holdtime']):
						logging.warning('savereplay - Memcache set failed')
		
		# return
		time_taken =  time.time() - start_time;
		self.debug += '('+str(time_taken)+')'
		self.response.headers['Content-Type'] = 'text/html'
		if self.respn == '': self.respn = '""'
		if self.request.get('debug'):
			self.response.write('{"response":'+self.respn+',"error":"'+self.error+'", "debug":"'+self.debug+'"}')
		else:
			self.response.write('{"response":'+self.respn+',"error":"'+self.error+'"}')
		
		
	def post(self):
		self.get()
		
		