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
			player = Player.getplayer_as_obj(self, uuid)						# get player from Player model class helper, specified by uuid
			if player is None:													# if no player data returned or doesn't exist
				player = Player(parent=db.Key.from_path('Player', config.db['playerdb_name']))	# create a new player state data
				player.uuid = uuid # = Utils.geneuuid(self, 'random')			# assign uuid
				# and assign all player state
				player.state_obj = {}
				player.state_obj['token'] 		= token
				player.state_obj['name']		= name
				player.state_obj['photo']		= photo
				player.state_obj['platinum'] 	= platinum
				player.state_obj['gold'] 		= gold
				player.state_obj['xp'] 			= xp
				player.state_obj['fuel'] 		= fuel
				player.state_obj['fuel_max'] 	= fuel_max
			else:																# but if player does exist
				if token:														# if token is provided
					player.state_obj['token'] = token							# assign token to player state
				player.state_obj['name'] = name									# assign name
				player.state_obj['photo'] = photo								# assign photo url
				
			if Player.setplayer_as_obj(self, player):							# write down to database
				self.error = ''													# then obviously, no error
				Player.compose_player(self, player)								# compose the entire player state to return
			else:																# but if write down to database was failed
				self.error = 'unable to insert/update player data.'				# inform user bia error message
						
		# calculate time taken and return the result
		time_taken =  time.time() - start_time
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))
		
	# do exactly as get() does
	def post(self):
		self.get()