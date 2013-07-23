""" advicechecklist action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae


	Description
	---------------------------------------------------------------
	I am an API to add checklist to advice_clicklist and return


	Input:
	---------------------------------------------------------------
	required: passwd, uuid
	optional: version, lang, checklist (string separate by commas)


	Output:
	---------------------------------------------------------------
	updated with added advice checklist in player's state

"""

# built-in libraries
import webapp2
import logging
import time

# config
from config import config

# include
from helpers.utils import Utils
from models.Data import Data
from models.Player import Player
from models.Building import Building

# class implementation
class advicechecklist(webapp2.RequestHandler):

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
		guid = self.request.get('guid')
		version = config.data_version['building']
		if self.request.get('version'):
			version = self.request.get('version')
		lang = config.server["defaultLanguage"]
		if self.request.get('lang'):
			lang = self.request.get('lang')
		checklist = self.request.get('checklist')

		# check password
		if self.error == '' and passwd != config.testing['passwd']:
			self.error = 'passwd is incorrect.'

		start_time = time.time()												# start count

		# logic variables
		player = None

		# if error, skip this
		if self.error == '':
			player = Player.getplayer(self, uuid)

		if self.error == '' and player is not None and guid != '':
			logging.info(guid + '==' + player.state_obj['guid'])
			if guid != player.state_obj['guid']:
				player = None
				self.error = config.error_message['dup_login']

		if self.error == '' and player is not None:

			_checklist = ''
			try:
				_checklist = player.state_obj['advice_checklist']
			except KeyError:
				player.state_obj['advice_checklist'] = _checklist

			if checklist:
				if _checklist == '':
					_checklist = checklist
				else:
					_checklist = _checklist.rstrip(',') + ',' + checklist.lstrip(',')

				player.state_obj['advice_checklist'] = _checklist

			# update timestamp for player
			player.state_obj['updated'] = start_time
			Player.setplayer(self, player)

			self.respn = '{"state":{"advice_checklist":"'+player.state_obj['advice_checklist']+'"}}'

		# calculate time taken and return the result
		time_taken = time.time() - start_time
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))

	# do exactly as get() does
	def post(self):
		self.get()