import webapp2
import json
import logging
import math
import random
import time

logging.basicConfig(filename='testing.log', level=logging.INFO)

# built-in libraries
from random 		import randint
from datetime		import date, datetime

# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache

# config
from config			import config

# models
from models.Player 	import Player
from models.Score 	import Score

class _populate(webapp2.RequestHandler):
	
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
		
	def geneuuid(self, par_name):
		if self.request.get(par_name):
			return self.request.get(par_name)
		else:
			now = datetime.now()
			return now.strftime('%S%y%M%m%H%d')+str(randint(1, 100))
		
		
	def get(self):
	
		self.reset()
		
		# validate
		passwd	= self.required('passwd')
		start	= self.required('start')
		num		= self.required('num')
		
		if self.error == '' and passwd != config.testing['passwd']:
			self.error = 'passwd is incorrect.'
			
		start_time = time.time()
		
		if self.error == '':
			j=0
			l=0
			for i in range(int(start), int(start)+int(num)):
				player = Player(parent=db.Key.from_path('Player', config.db['playerdb_name']))
				player.uuid 	= '_test'+str(i+1) #self.geneuuid('random')
				player.state	= '{"name":"_test'+str(i+1)+'",'
				player.state   += '"photo":"'+config.testing['photosample']+'"}'
				if player.put():
					j = j+1
					for k in config.testing['track']:
						for t in config.leaderboard['type']:
							score = Score(parent=db.Key.from_path('Score', config.db['scoredb_name']))
							score.uuid 	= player.uuid
							score.type 	= k
							score.point = float(randint(50, 200))
							score.data	= '{'
							score.data += '"name":"'	+'_test'+str(i+1)+	'",'
							score.data += '"photo":"'	+config.testing['photosample']+	'",'
							score.data += '"replay":"'	+config.testing['replaysample']+	'"'
							score.data += '}'
			
							start_date = date.today().replace(day=1, month=1, year=2013).toordinal()
							end_date = date.today().toordinal()
							random_day = date.fromordinal(random.randint(start_date, end_date))

							if t == 'weekly':
								score.created_dwmy = '0-'+str(int(math.ceil(random_day.day / 7)))+'-'+str(random_day.month)+'-'+str(random_day.year)
							else:
								score.created_dwmy = str(random_day.day)+'-'+str(int(math.ceil(random_day.day / 7)))+'-'+str(random_day.month)+'-'+str(random_day.year)
							
							if score.put():
								l = l + 1;
			
			time_taken =  time.time() - start_time;
			logging.info(str(j)+' users were added, '+str(l)+' scores were added. ('+str(time_taken)+' secs)')
			self.respn = '"'+str(j)+' users were added, '+str(l)+' scores were added. ('+str(time_taken)+' secs)"'
		
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
		
		
class _cleanup(webapp2.RequestHandler):
	
	error = ''
	respn = ''
	debug = ''
	
	def reset(self):
		self.error = '';
		self.respn = '';
		self.debug = '';
	
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
		start	= self.required('start')
		num		= self.required('num')
		
		if self.error == '' and passwd != config.testing['passwd']:
			self.error = 'passwd is incorrect.'
		
		start_time = time.time()
		
		if self.error == '':
			j=0
			l=0
			for i in range(int(start), int(start)+int(num)):
				players = Player.all().filter('uuid =', '_test'+str(i+1)).ancestor(db.Key.from_path('Player', config.db['playerdb_name'])).fetch(1);
				if len(players) >= 1:
					scores = Score.all().filter('uuid =', players[0].uuid).ancestor(db.Key.from_path('Score', config.db['scoredb_name'])).fetch(len(config.testing['track'])*len(config.leaderboard['type']));
					for score in scores:
						score.delete()
						l = l + 1
							
					players[0].delete()
					j = j + 1;
					
			time_taken =  time.time() - start_time;
			logging.info(str(j)+' users were deleted, '+str(l)+' scores were deleted. ('+str(time_taken)+' secs)')
			self.respn = '"'+str(j)+' users were deleted, '+str(l)+' scores were deleted. ('+str(time_taken)+' secs)"'
			
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