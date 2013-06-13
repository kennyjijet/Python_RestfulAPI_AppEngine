""" loadplayer action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae
	

	Description
	---------------------------------------------------------------
	I am an API to get player state, (partial data is an optional)

	
	Input:
	---------------------------------------------------------------
	required: uuid
	optional: specific

	
	Output:
	---------------------------------------------------------------
	player uuid and entire player state
	or
	partial player state data 
	
"""

# built-in libraries
import webapp2
import json
import logging
import time

# include
from helpers.utils import Utils
from models.Player import Player

# class implementation
class loadplayer(webapp2.RequestHandler):
	
	# standard variables
	sinfo = ''
	respn = ''
	error = ''
	debug = ''
		
	# get function implementation
	def get(self):
		Utils.reset(self)														# reset/clean standard variables
		
		# validate and assign parameters
		uuid = Utils.required(self, 'uuid')
		specific = self.request.get('specific')
		start_time = time.time()                                                # start count
			
		# if error, skip this
		if self.error == '':
			player = Player.getplayer(self, uuid)								# get player state from Player helper class, specified by uuid
			if player is not None:												# if have some data returned					
				if specific is not None and specific != '':						# and if user wants to request partial data, (by specifying whatever they want)
					Player.compose_player_partial(self, player, specific)		# compose partial data to return
				else:															# but if not
					Player.compose_player(self, player)							# just compose the entire player state to return
				
		# calculate time taken and return result
		time_taken = time.time() - start_time
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))
		
	# do exactly as get() does
	def post(self):
		self.get()