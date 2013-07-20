""" carlist action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae


	Description
	---------------------------------------------------------------
	I am an API to get list of player's cars


	Input:
	---------------------------------------------------------------
	required: passwd, uuid
	optional: lang, version


	Output:
	---------------------------------------------------------------
	list of player's cars

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
from models.Car import Car

# class implementation
class carlist(webapp2.RequestHandler):

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
		version = config.data_version['building']
		if self.request.get('version'):
			version = self.request.get('version')
		lang = config.server["defaultLanguage"]
		if self.request.get('lang'):
			lang = self.request.get('lang')
		uuid = Utils.required(self, 'uuid')

		# check password
		if self.error == '' and passwd != config.testing['passwd']:
			self.error = 'passwd is incorrect.'

		start_time = time.time()												# start count

		# logical variables
		player = None
		mycars = None

		# if error, skip this
		if self.error == '':
			player = Player.getplayer(self, uuid)

		if self.error == '' and player is not None:
			mycars = Car.list(self, uuid)
			self.respn = '['
			for _car in mycars:
				self.respn += Car.compose_mycar('', _car) + ','
			self.respn = self.respn.rstrip(',') + ']'

		# calculate time taken and return the result
		time_taken = time.time() - start_time
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))

	# do exactly as get() does
	def post(self):
		self.get()