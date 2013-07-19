""" challengeupdate action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae


	Description
	---------------------------------------------------------------
	I am an API to update a challenge


	Input:
	---------------------------------------------------------------
	required: passwd, uuid, chid, type, cuid, laptime, replay
	optional:


	Output:
	---------------------------------------------------------------
	challenge data

"""

# built-in libraries
import webapp2
import logging
import time

# config
from config import config

# include
from helpers.utils import Utils
from models.Player import Player
from models.Challenge import Challenge

# class implementation
class challengeupdate(webapp2.RequestHandler):

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
		chid = Utils.required(self, 'chid')
		type = Utils.required(self, 'type')
		cuid = Utils.required(self, 'cuid')
		laptime = Utils.required(self, 'laptime')
		replay = Utils.required(self, 'replay')

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
			challenge = Challenge.Update(self, chid, type, player.fbid, cuid, laptime, replay)
			if challenge is not None:
				Challenge.ComposeChallenge(self, challenge)

			# update timestamp for player
			if challenge.manual_update is True:
				player.info_obj['updated'] = start_time
				Player.setplayer(self, player)

		# calculate time taken and return the result
		time_taken = time.time() - start_time
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))

	# do exactly as get() does
	def post(self):
		self.get()