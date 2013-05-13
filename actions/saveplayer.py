""" saveplayer action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae
	

	Description
	---------------------------------------------------------------
	I am an API to set/save/update player state

	
	Input:
	---------------------------------------------------------------
	required: passwd, name, photo
	optional: uuid, token

	
	Output:
	---------------------------------------------------------------
	player uuid and entire player state
	
	
"""

# built-in libraries
import webapp2
import json
import logging
import time

# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache

# config
from config			import config

# include
from helpers.utils		import Utils
from models.Player 	import Player

# class implementation
class saveplayer(webapp2.RequestHandler):
	
	# standard variables
	sinfo = ''
	respn = ''
	error = ''
	debug = ''
	
	# get function implementation
	def get(self):
		Utils.reset(self)														# reset/clean standard variables
		
		# validate and assign parameters
		passwd	= Utils.required(self, 'passwd')
		uuid	= Utils.geneuuid(self, 'uuid')
		token	= self.request.get('token')
		name	= Utils.required(self, 'name')
		photo	= Utils.required(self, 'photo')
		platinum= 10
		gold	= 5000
		xp		= 0
		fuel	= 5
		fuel_max= 20 
		
		
		if self.error == '' and passwd != config.testing['passwd']:				# if password is incorrect
			self.error = 'passwd is incorrect.'									# inform user via error message
		start_time = time.time()												# start count 
		
		# if error, skip this
		if self.error == '':
			player = Player.getplayer(self, uuid)								# get player from Player model class helper, specified by uuid
			if player is None:													# if no player data returned or doesn't exist
				player = Player(parent=db.Key.from_path('Player', config.db['playerdb_name']))	# create a new player state data
				player.uuid = uuid # = Utils.geneuuid(self, 'random')			# assign uuid
				player.state  = '{'												# and assign all player state
				player.state += '"token":"'		+token+		'",'
				player.state += '"name":"'		+name+			'",'
				player.state += '"photo":"'		+photo+			'",'
				player.state += '"platinum":'	+str(platinum)+	','
				player.state += '"gold":'		+str(gold)+		','
				player.state += '"xp":'			+str(xp)+		','
				player.state += '"fuel":'		+str(fuel)+		','
				player.state += '"fuel_max":'	+str(fuel_max)
				player.state += '}'
			else:																# but if player does exist
				player_obj = json.loads(player.state)							# parse player state as plaintext to json object, in order to manipulate
				if token:														# if token is provided
					player_obj['token'] = token									# assign token to player state
				player_obj['name'] = name										# assign name
				player_obj['photo'] = photo										# assign photo url
				player.state = json.dumps(player_obj)							# and put it back into plaintext
				
			if player.put():													# write down to database
				self.error = ''													# then obviously, no error
				Player.compose_player(self, player)								# compose the entire player state to return
			else:																# but if write down to database was failed
				self.error = 'unable to insert/update player data.'				# inform user bia error message
		
			# afterall we need to save this result to memcahce ,, avoiding 
			memcache.delete(config.db['playerdb_name']+'.'+uuid)				# we need to delete it first, bacause it may remain and reject to set a new memecache
			if not memcache.add(config.db['playerdb_name']+'.'+uuid, player, config.memcache['holdtime']): # then add into memcache
				logging.warning('saveplayer - Memcache set failed')				# log it, if failed to set memcache
						
		# calculate time taken and return the result
		time_taken =  time.time() - start_time
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))
		
	# do exactly as get() does
	def post(self):
		self.get()