import webapp2
import json
import logging
import math
import time

logging.basicConfig(filename='getleaderboard.log', level=logging.INFO)

from datetime 		import datetime, date, timedelta

# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache

# config
from config			import config

# models
from models.Player 	import Player
from models.Score 	import Score

class getleaderboard(webapp2.RequestHandler):
	
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
		type 	= self.required('type')
		track 	= self.required('track')
		
		#if self.error == '' and passwd != config.testing['passwd']:
		#	self.error = 'passwd is incorrect.'
		
		start_time = time.time()
					
		if self.error == '':
			_memcache = False
			leaderboard = memcache.get(config.db['scoredb_name']+'.'+track+'.'+type)
			if leaderboard is None:
				leaderboard = Score.all().filter('type =', track)
				if type == 'friends':
					leaderboard = leaderboard.filter('created_dwmy = ', str(date.today().day)+'-'+str(int(math.ceil(date.today().day / 7)))+'-'+str(date.today().month)+'-'+str(date.today().year))
				elif type == 'weekly':
					leaderboard = leaderboard.filter('created_dwmy = ', '0-'+str(int(math.ceil(date.today().day / 7)))+'-'+str(date.today().month)+'-'+str(date.today().year))
				else: #daily
					leaderboard = leaderboard.filter('created_dwmy = ', str(date.today().day)+'-'+str(int(math.ceil(date.today().day / 7)))+'-'+str(date.today().month)+'-'+str(date.today().year))
				
				leaderboard = leaderboard.order('point').ancestor(db.Key.from_path('Score', config.db['scoredb_name'])).fetch(config.leaderboard['fetch_num']);
			else:
				_memcache = True
				
			if leaderboard is not None:
				rank = 0
				self.respn = '['
				for leader in leaderboard:
					leader_obj = json.loads(leader.data)
					rank = rank+1
					self.respn += '{'
					self.respn += '"rank":"'	+str(rank)+		'",'
					self.respn += '"uuid":"'	+leader.uuid+	'",'
					self.respn += '"name":"'	+leader_obj['name']+	'",'
					self.respn += '"photo":"'	+leader_obj['photo']+	'",'
					#self.respn += '"track":"'	+leader.type+			'",'
					self.respn += '"score":"'	+str(leader.point)+ 	'"'
					#self.respn += '"data":'	+leader.data+			''
					self.respn += '},'
				self.respn = self.respn.rstrip(',') + ']'
				
				if _memcache==False:
					if not memcache.add(config.db['scoredb_name']+'.'+track+'.'+type, leaderboard, config.memcache['holdtime']):
						logging.warning('getleaderboard - Memcache set failed')
		
		# return
		time_taken =  time.time() - start_time
		self.debug += '('+str(time_taken)+')'
		self.response.headers['Content-Type'] = 'text/html'
		if self.respn == '': self.respn = '""'
		if self.request.get('debug'):
			self.response.write('{"response":'+self.respn+',"error":"'+self.error+'", "debug":"'+self.debug+'"}')
		else:
			self.response.write('{"response":'+self.respn+',"error":"'+self.error+'"}')
		
		
	def post(self):
		self.get()
		