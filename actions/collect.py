""" collect action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae


	Description
	---------------------------------------------------------------
	I am an API to collect resource produced from building


	Input:
	---------------------------------------------------------------
	required: passwd, uuid, inid
	optional: version


	Output:
	---------------------------------------------------------------
	updated with added resource player state, and collected building info

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
class collect(webapp2.RequestHandler):

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
		uuid = Utils.required(self, 'uuid')
		inid = Utils.required(self, 'inid')

		# check password
		if self.error == '' and passwd != config.testing['passwd']:
			self.error = 'passwd is incorrect.'

		start_time = time.time()												# start count

		# logic variables
		player = None
		buildings = None
		mybuilding = None
		res_produced = 0

		# if error, skip this
		if self.error == '':
			player = Player.getplayer_as_obj(self, uuid)

		if self.error == '' and player is not None:
			buildings = Data.getbuildings(self, version)

		if self.error == '' and buildings is not None:
			mybuilding = Building.getmybuilding(self, uuid, inid)

		if self.error == '' and mybuilding is not None:
			_name = str(mybuilding.itid)
			_pos = mybuilding.itid.find('.', len(mybuilding.itid)-4)
			_bui = mybuilding.itid[0:_pos]
			_lev = mybuilding.itid[_pos+1:len(mybuilding.itid)]
			_upd = False
			if mybuilding.status == Building.BuildingStatus.PENDING:
				if mybuilding.timestamp + (buildings.as_obj[_bui][_lev]['wait']*60) <= start_time:
					mybuilding.timestamp = int(start_time)
					mybuilding.status = Building.BuildingStatus.REWARD
					_upd = True
			elif mybuilding.status == Building.BuildingStatus.REWARD:
				mybuilding.status = Building.BuildingStatus.REWARDED
				_upd = True
			if mybuilding.status == Building.BuildingStatus.REWARD or mybuilding.status == Building.BuildingStatus.REWARDED or mybuilding.status == Building.BuildingStatus.PRODUCED_PARTIAL:
				time_delta = int((start_time - mybuilding.timestamp)/60)
				if time_delta > buildings.as_obj[_bui][_lev]['interval']:
					mybuilding.status = Building.BuildingStatus.PRODUCED_PARTIAL
					_upd = True
				res_produced = (time_delta / buildings.as_obj[_bui][_lev]['interval']) * buildings.as_obj[_bui][_lev]['units_made']
				if res_produced >= buildings.as_obj[_bui][_lev]['capacity']:
					res_produced = buildings.as_obj[_bui][_lev]['capacity']
					mybuilding.status = Building.BuildingStatus.PRODUCED
					_upd = True
			if mybuilding.status == Building.BuildingStatus.PRODUCED_PARTIAL or mybuilding.status == Building.BuildingStatus.PRODUCED:
				try:
					player.state_obj[buildings.as_obj[_bui][_lev]['resource']] += res_produced
					if Player.setplayer_as_obj(self, player):
						mybuilding.status = Building.BuildingStatus.REWARDED
						mybuilding.timestamp = int(start_time)
						_upd = True
				except KeyError:
					self.error = 'resource='+buildings.as_obj[_bui][_lev]['resource']+' doesn\'t exist in player properties!'

			if _upd is True:
				Building.setmybuilding(self, mybuilding)

			if self.error == '':
				self.respn = '{"state":'+player.state+', "buildings":['
				self.respn = Building.compose_mybuilding(self.respn, mybuilding)
				self.respn = self.respn.rstrip(',') + ']'
				self.respn += '}'

		# calculate time taken and return the result
		time_taken = time.time() - start_time
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))

	# do exactly as get() does
	def post(self):
		self.get()