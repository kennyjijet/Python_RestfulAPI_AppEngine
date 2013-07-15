""" setpntoken action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae
	

	Description
	---------------------------------------------------------------
	I am an API to set token for player in player state

	
	Input:
	---------------------------------------------------------------
	required: passwd, uuid, token
	optional: 

	
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
from google.appengine.api import memcache

# config
from config			import config

# include
from helpers.utils		import Utils
from models.Player		import Player

# class implementation
class setpntoken(webapp2.RequestHandler):
	
	# standard variables
	sinfo = ''
	respn = ''
	error = ''
	debug = ''
	
	# get function implementation
	def get(self):
		Utils.reset(self)											# reset/clean standard variables
		
		# validate and assign parameters
		passwd = Utils.required(self, 'passwd')
		uuid = Utils.required(self, 'uuid')
		token = Utils.required(self, 'token')
		
		# required password to process this action
		if self.error == '' and passwd != config.testing['passwd']:
			self.error = 'passwd is incorrect.'
			
		start_time = time.time()									# start count 
		
		# if any error, skip this
		if self.error == '':
			player = Player.getplayer(self, uuid)			# get player as object
		
		# if any error on player is none
		if self.error == '' and player is not None:
			player.info_obj['token'] = token
			# update timestamp for player
			player.info_obj['updated'] = start_time
			if Player.setplayer(self, player):
				Player.compose_player_info(self, player)
			else:
				self.error = 'unable to update player data (token).'
	
		# calculate time taken and return the result
		time_taken = time.time() - start_time
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))
		
	# do exactly as get() does
	def post(self):
		self.get()