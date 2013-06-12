""" buybuilding action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae


	Description
	---------------------------------------------------------------
	I am an API to get list of buildings that user can buy


	Input:
	---------------------------------------------------------------
	required: passwd, uuid, itid
	optional: lang, version, userdata


	Output:
	---------------------------------------------------------------
	list of buildings

"""

# built-in libraries
import webapp2
import logging
import time
import json

# google's libraries
from google.appengine.ext import db

# config
from config import config

# include
from helpers.utils import Utils
from models.Data import Data
from models.Item import Item
from models.Player import Player
from models.Building import Building

# class implementation
class buybuilding(webapp2.RequestHandler):

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
		version = config.data_version['buildings']
		if self.request.get('version'):
			version = self.request.get('version')
		lang = config.server["defaultLanguage"]
		if self.request.get('lang'):
			lang = self.request.get('lang')
		uuid = Utils.required(self, 'uuid')
		itid = Utils.required(self, 'itid')
		location = Utils.required(self, 'location')

		# check password
		if self.error == '' and passwd != config.testing['passwd']:
			self.error = 'passwd is incorrect.'

		start_time = time.time()												# start count

		# logical variables
		player = None
		buildings = None
		building = None

		# if error, skip this
		if self.error == '':
			player = Player.getplayer_as_obj(self, uuid)

		if self.error == '' and player is not None:
			buildings = Data.getbuildings(self, float(version))

		if self.error == '' and buildings is not None:
			_name = str(itid)
			_pos = itid.find('.', len(itid)-4)
			_bui = itid[0:_pos]
			_lev = itid[_pos+1:len(itid)]
			logging.info(_bui + ' ' + _lev)

			try:
				building = buildings.as_obj[_bui][_lev]
			except KeyError:
				self.error = itid + " was not found!"

		if self.error == '' and building is not None:
			if player.state_obj['cash'] >= building['cost']:
				player.state_obj['cash'] -= building['cost']
				if Player.setplayer_as_obj(self, player):
					mybuilding = Building.newbuilding(self)
					mybuilding.uuid = uuid
					mybuilding.itid = itid
					mybuilding.inid = Utils.genanyid(self, 'b')
					mybuilding.status = Building.BuildingStatus.PENDING
					mybuilding.location = location
					mybuilding.timestamp = int(start_time)
					Building.setmybuilding(self, mybuilding)
					self.respn = '{"state":'+player.state+','
					self.respn += '"buildings":['
					self.respn = Building.compose_mybuilding(self.respn, mybuilding)
					self.respn = self.respn.rstrip(',') + ']'
					self.respn += '}'
			else:
				self.respn = '{"warning":"not enough cash!"}'

		# calculate time taken and return the result
		time_taken = time.time() - start_time
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))

	# do exactly as get() does
	def post(self):
		self.get()