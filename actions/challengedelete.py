""" challengedelete action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae


	Description
	---------------------------------------------------------------
	I am an API to delete a challenge or delete all give user's challenges


	Input:
	---------------------------------------------------------------
	required: passwd, uuid,
	optional: chid


	Output:
	---------------------------------------------------------------
	result = success/failed

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
class challengedelete(webapp2.RequestHandler):

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
		chid = self.request.get('chid')

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
			if chid:
				if Challenge.DeleteById(self, chid):
					self.respn = '{"result":"delete successfully"}'
				else:
					self.respn = '{"result":"Challenge Id='+chid+' could not be found, nothing was deleted"}'
			else:
				if Challenge.DeleteByUserId(self, player.fbid):
					self.respn = '{"result":"delete successfully"}'
				else:
					self.respn = '{"result":"nothing was deleted"}'

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