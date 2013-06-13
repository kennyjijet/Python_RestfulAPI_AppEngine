""" saveplayer action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae
	

	Description
	---------------------------------------------------------------
	I am an API to set/save/update player state

	
	Input:
	---------------------------------------------------------------
	required: passwd,
	optional: uuid, name, photo, token

	
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
from config import config

# include
from helpers.utils import Utils
from models.Player import Player

# class implementation
class saveplayer(webapp2.RequestHandler):
	# standard variables
	sinfo = ''
	respn = ''
	error = ''
	debug = ''

	# get function implementation
	def get(self):
		Utils.reset(self)                                                        # reset/clean standard variables

		# validate and assign parameters
		passwd = Utils.required(self, 'passwd')

		uuid = self.request.get('uuid')
		token = self.request.get('token')
		name = Utils.genanyid(self, 'Guest')
		if self.request.get('name'):
			name = self.request.get('name')
		photo = "http://graph.facebook.com/pluspingya/picture?type=square"
		if self.request.get('photo'):
			photo = self.request.get('photo')

		gold = 10
		cash = 5000
		fuel = 5
		tire = 5
		battery = 5
		oil = 5
		brake = 5

		if self.error == '' and passwd != config.testing['passwd']:                	# if password is incorrect
			self.error = 'passwd is incorrect.'                                    	# inform user via error message

		start_time = time.time()                                                	# start count

		# if error, skip this
		if self.error == '':
			player = Player.getplayer(self, uuid)                        			# get player from Player model class helper, specified by uuid
			if player is None:                                                    	# if no player data returned or doesn't exist
				player = Player(parent=db.Key.from_path('Player', config.db['playerdb_name']))    # create a new player state data
				player.uuid = Utils.genanyid(self, 'u')                        		# assign uuid
				# and assign all player info and state
				player.info_obj = {'uuid': player.uuid, 'token': token, 'name': name, 'photo': photo}
				player.state_obj = {'gold': gold, 'cash': cash, 'fuel': fuel, 'tire': tire, 'battery': battery, 'oil': oil, 'brake': brake}
			else:                                                                	# but if player does exist
				if token:                                                        	# if token is provided
					player.state_obj['token'] = token                            	# assign token to player state
				player.info_obj['name'] = name                                    	# assign name
				player.info_obj['photo'] = photo                                	# assign photo url
				# try .. cash and assign new property
				try:
					gold = player.state_obj['gold']
				except KeyError:
					player.state_obj['gold'] = gold
				try:
					cash = player.state_obj['cash']
				except KeyError:
					player.state_obj['cash'] = cash
				try:
					fuel = player.state_obj['fuel']
				except KeyError:
					player.state_obj['fuel'] = fuel
				try:
					tire = player.state_obj['tire']
				except KeyError:
					player.state_obj['tire'] = tire
				try:
					battery = player.state_obj['battery']
				except KeyError:
					player.state_obj['battery'] = battery
				try:
					oil = player.state_obj['oil']
				except KeyError:
					player.state_obj['oil'] = oil
				try:
					brake = player.state_obj['brake']
				except KeyError:
					player.state_obj['brake'] = brake

			if Player.setplayer(self, player):                            # write down to database
				self.error = ''                                                    # then obviously, no error
				Player.compose_player(self, player)                                # compose the entire player state to return
			else:                                                                # but if write down to database was failed
				self.error = 'unable to insert/update player data.'                # inform user bia error message

		# calculate time taken and return the result
		time_taken = time.time() - start_time
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))

	# do exactly as get() does
	def post(self):
		self.get()