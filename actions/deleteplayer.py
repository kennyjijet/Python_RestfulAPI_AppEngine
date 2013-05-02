import webapp2
import json
import logging
import time

logging.basicConfig(filename='deleteplayer.log', level=logging.INFO)

# built-in libraries
from random 		import randint
from datetime		import datetime

# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache

# config
from config			import config

# models
from models.Player 	import Player
from models.Score 	import Score
from models.Item	import Item
# include
from controllers.Core	import Core
from helpers.utils		import Utils

class deleteplayer(webapp2.RequestHandler):
	
	sinfo = ''
	respn = ''
	error = ''
	debug = ''
		
	def get(self):
		Utils.reset(self)
		
		# validate
		passwd	= Utils.required(self, 'passwd')
		uuid	= Utils.required(self, 'uuid')
		
		if self.error == '' and passwd != config.testing['passwd']:
			self.error = 'passwd is incorrect.'
			
		start_time = time.time()
		
		if self.error == '':
			
			players = Player.all().filter('uuid =', uuid).ancestor(db.Key.from_path('Player', config.db['playerdb_name'])).fetch(1);
			didDelete = False
			for player in players:
				
				scores = Score.all().filter('uuid =', player.uuid).ancestor(db.Key.from_path('Score', config.db['scoredb_name']));
				for score in scores:
					score.delete()
				memcache.delete(config.db['scoredb_name']+'.'+uuid)
					
				items = Item.all().filter('uuid =', player.uuid).ancestor(db.Key.from_path('Item', config.db['itemdb_name']));
				for item in items:
					item.delete()
				memcache.delete(config.db['itemdb_name']+'.'+uuid)
				
				player.delete()
				memcache.delete(config.db['playerdb_name']+'.'+uuid)
				didDelete = True

			if didDelete == True:
				self.respn =  '"'+uuid+' was deleted successfully."'
			else:
				self.error = uuid+' does not exist in Database.'
				
		# return
		time_taken =  time.time() - start_time;
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))
		
	
	def post(self):
		self.get()