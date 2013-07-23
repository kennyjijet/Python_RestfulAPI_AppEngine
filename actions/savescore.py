import webapp2
import json
import logging
import math
import time

logging.basicConfig(filename='savescore.log', level=logging.INFO)

# built-in libraries
from datetime import datetime, date

# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache

# config
from config			import config

# models
from models.Player 	import Player
from models.Score 	import Score

class savescore(webapp2.RequestHandler):
	
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
		uuid 	= self.required('uuid')
		guid = self.request.get('guid')
		name	= self.required('name')
		photo	= self.request.get('photo')
		track 	= self.required('track')
		point 	= self.required('score')
		replay	= self.required('replay')
		
		if self.error == '' and passwd != config.testing['passwd']:
			self.error = 'passwd is incorrect.'
		
		start_time = time.time()
		
		if self.error == '':
			_memcache = False			
			player = memcache.get(config.db['playerdb_name']+'.'+uuid)
			if player is None:
				players = Player.all().filter('uuid =', uuid).ancestor(db.Key.from_path('Player', config.db['playerdb_name'])).fetch(1);
				if len(players)>=1:
					player = players[0]
				else:
					self.error = 'uuid='+uuid+' was not found.'
					player = None
			else:
				_memcache = True
				
			if player is not None:
				if _memcache==False:
					if not memcache.add(config.db['playerdb_name']+'.'+uuid, player, config.memcache['holdtime']):
						logging.warning('savescore - Memcache set failed')
		
		if self.error == '':
			
			today = datetime.today()
			for t in config.leaderboard['type']:
				_memcache = False
				score = memcache.get(config.db['scoredb_name']+'.'+uuid+'.'+str(today.date())+'.'+track+'.'+t)
				if score is None:
					scores = Score.all().filter('uuid =', uuid).filter('type =', track)
					if t == 'daily':
						scores = scores.filter('created_dwmy = ', str(date.today().day)+'-'+str(int(math.ceil(date.today().day / 7)))+'-'+str(date.today().month)+'-'+str(date.today().year))
					elif t == 'weekly':
						scores = scores.filter('created_dwmy = ', '0-'+str(int(math.ceil(date.today().day / 7)))+'-'+str(date.today().month)+'-'+str(date.today().year))
					else: #monthly
						scores = scores.filter('created_dwmy = ', '0-0-'+str(date.today().month)+'-'+str(date.today().year))
					scores = scores.ancestor(db.Key.from_path('Score', config.db['scoredb_name'])).fetch(1);
					
					if len(scores)>=1:
						score = scores[0]
					else:
						score = Score(parent=db.Key.from_path('Score', config.db['scoredb_name']))
						
				else:
					_memcache = True
				
				if score.point is not None:
					if score.point < float(point):
						self.respn = '{"ignored_action":"your existing score is better than new score (or just same score)."}'
						score = None
				
				if score is not None:
				
					score.uuid		= uuid
					score.type 		= track
					score.point 	= float(point)
					
					score.data		= '{'
					score.data	   += '"name":"'	+name+		'",'
					score.data	   += '"photo":"'	+photo+		'",'
					score.data	   += '"replay":"'	+replay+	'"'
					score.data	   += '}'
					
					if t == 'weekly':
						score.created_dwmy = '0-'+str(int(math.ceil(date.today().day / 7)))+'-'+str(date.today().month)+'-'+str(date.today().year)
					else: 
						score.created_dwmy = str(date.today().day)+'-'+str(int(math.ceil(date.today().day / 7)))+'-'+str(date.today().month)+'-'+str(date.today().year)
					
					if score.put():
						self.respn	= '{'
						self.respn  += '"uuid":"'	+uuid+	'",'
						self.respn  += '"track":"'	+track+	'",'
						self.respn  += '"score":"'	+str(score.point)+	'",'
						self.respn  += '"name":"'	+name+			'",'
						self.respn  += '"photo":"'	+photo+			'",'	
						self.respn  += '"replay":"'	+replay+		'"'
						self.respn  += '}'
					else:
						self.error = "unable to insert/update score data."
				
					if _memcache==False:
						if not memcache.add(config.db['scoredb_name']+'.'+uuid+'.'+str(today.date())+'.'+track+'.'+t, score, config.memcache['holdtime']):
							logging.warning('savescore - Memcache set failed')
						
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
		
		