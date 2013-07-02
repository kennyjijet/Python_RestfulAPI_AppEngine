""" getplayerdata action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae


	Description
	---------------------------------------------------------------
	I am an API to get player data, inventory, or both optionally.


	Input:
	---------------------------------------------------------------
	required: passwd, uuid, get = list of data, separate by commas
	optional: specific


	Output:
	---------------------------------------------------------------
	player data, inventory, or both

"""

# built-in libraries
import webapp2
import json
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
class getplayerdata(webapp2.RequestHandler):

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
		get = Utils.required(self, 'get')
		version = config.data_version['buildings']
		if self.request.get('version'):
			version = self.request.get('version')
		lang = config.server["defaultLanguage"]
		if self.request.get('lang'):
			lang = self.request.get('lang')

		if self.error == '' and passwd != config.testing['passwd']:                	# if password is incorrect
			self.error = 'passwd is incorrect.'                                    	# inform user via error message

		start_time = time.time()                                                # start count

		# if error, skip this
		if self.error == '':
			player = Player.getplayer(self, uuid)								# get player state from Player helper class, specified by uuid

		if self.error == '' and player is not None:												# if have some data returned
			self.respn = '{'
			gets = get.split(',')
			for item in gets:
				if item == 'info':
					self.respn += '"info":'+player.info+','
				elif item == 'state':
					self.respn += '"state":'+player.state+','
				elif item == 'building':
					buildings = Data.getbuildings(self, lang, version)
					mybuildings = Building.getmybuildings(self, uuid)
					if buildings is not None and mybuildings is not None:
						self.respn += '"building":['
						for mybuilding in mybuildings:
							# update building status, determine production
							_upd = False
							if mybuilding.status == Building.BuildingStatus.PENDING:
								if mybuilding.timestamp + (buildings.as_obj[mybuilding.itid][mybuilding.level-1]['build_time']*60) <= start_time:
									mybuilding.timestamp = int(start_time)
									mybuilding.status = Building.BuildingStatus.REWARD
									_upd = True
							elif mybuilding.status == Building.BuildingStatus.REWARD:
								mybuilding.status = Building.BuildingStatus.REWARDED
								_upd = True
							if mybuilding.status == Building.BuildingStatus.REWARD or mybuilding.status == Building.BuildingStatus.REWARDED or mybuilding.status == Building.BuildingStatus.PRODUCED_PARTIAL:
								time_delta = int((start_time - mybuilding.timestamp)/60)
								if time_delta > buildings.as_obj[mybuilding.itid][mybuilding.level-1]['resource_interval'] > 0:
									mybuilding.status = Building.BuildingStatus.PRODUCED_PARTIAL
									_upd = True
									res_produced = (time_delta / buildings.as_obj[mybuilding.itid][mybuilding.level-1]['resource_interval']) * buildings.as_obj[mybuilding.itid][mybuilding.level-1]['resource_produced']
									if res_produced >= buildings.as_obj[mybuilding.itid][mybuilding.level-1]['resource_capacity']:
										res_produced = buildings.as_obj[mybuilding.itid][mybuilding.level-1]['resource_capacity']
										mybuilding.status = Building.BuildingStatus.PRODUCED
										_upd = True
							if _upd is True:
								Building.setmybuilding(self, mybuilding)
							self.respn = Building.compose_mybuilding(self.respn, mybuilding)
						self.respn = self.respn.rstrip(',') + '],'
			self.respn = self.respn.rstrip(',') + '}'

		# calculate time taken and return result
		time_taken = time.time() - start_time
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))

	# do exactly as get() does
	def post(self):
		self.get()