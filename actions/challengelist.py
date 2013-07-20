""" challengelist action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae


	Description
	---------------------------------------------------------------
	I am an API to get a list of all challengers and challenging


	Input:
	---------------------------------------------------------------
	required: passwd, uuid
	optional:


	Output:
	---------------------------------------------------------------
	list of challengers and challenging

"""

# built-in libraries
import webapp2
import logging
import time
import json

# config
from config import config

# include
from helpers.utils import Utils
from models.Player import Player
from models.Challenge import Challenge

# class implementation
class challengelist(webapp2.RequestHandler):

	# standard variables
	sinfo = ''
	respn = ''
	error = ''
	debug = ''

	# get function implementation
	def get(self):
		Utils.reset(self)														# reset/clean standard variables

		# validate and assign parameters
		passwd = Utils.required(self, 'passwd')
		uuid = Utils.required(self, 'uuid')

		# check password
		if self.error == '' and passwd != config.testing['passwd']:
			self.error = 'passwd is incorrect.'

		start_time = time.time()												# start count

		# logic variables
		player = None

		# if error, skip this
		if self.error == '':
			player = Player.getplayer(self, uuid)

		if self.error == '' and player is not None:
			self.respn = '{"challengers":['
			challengers = Challenge.GetChallengers(self, player.fbid)
			if challengers is not None:
				for _challenge in challengers:
					_gameObj = json.loads(_challenge.data)
					self.respn += '{'
					self.respn += '"chid":"'+_challenge.id+'",'
					self.respn += '"uidx":"'+_challenge.uid1+'",'
					self.respn += '"track":"'+_challenge.track+'"'
					self.respn += '},'
			self.respn = self.respn.rstrip(',') + '],"challenging":['
			challenging = Challenge.GetChallenging(self, player.fbid)
			if challenging is not None:
				for _challenge in challenging:
					_gameObj = json.loads(_challenge.data)
					self.respn += '{'
					self.respn += '"chid":"'+_challenge.id+'",'
					self.respn += '"uidx":"'+_challenge.uid2+'",'
					self.respn += '"track":"'+_challenge.track+'"'
					self.respn += '},'
			self.respn = self.respn.rstrip(',') + '],"completed":['
			completed = Challenge.GetCompleted(self, player.fbid)
			if completed is not None:
				for _challenge in completed:
					_gameObj = json.loads(_challenge.data)
					self.respn += '{'
					self.respn += '"chid":"'+_challenge.id+'",'
					#self.respn += '"uidx":"'+_challenge.uid1+'",'
					if player.fbid == _challenge.uid1:
						self.respn += '"uidx":"'+_challenge.uid2+'",'
					else:
						self.respn += '"uidx":"'+_challenge.uid1+'",'
					self.respn += '"track":"'+_challenge.track+'"'
					self.respn += '},'
			self.respn = self.respn.rstrip(',') + ']}'

			# update timestamp for player
			player.info_obj['updated'] = start_time
			Player.setplayer(self, player)

		# calculate time taken and return the result
		time_taken = time.time() - start_time
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))

	# do exactly as get() does
	def post(self):
		self.get()