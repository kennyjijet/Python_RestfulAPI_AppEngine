""" finishbuilding action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae


	Description
	---------------------------------------------------------------
	I am an API to fast track finish building


	Input:
	---------------------------------------------------------------
	required: passwd, uuid, inid
	optional: version


	Output:
	---------------------------------------------------------------
	updated with deducted gold and finished building info


"""

# built-in libraries
import webapp2
import logging
import time
import math

# config
from config import config

# include
from helpers.utils import Utils
from models.Data import Data
from models.Player import Player
from models.Building import Building

# class implementation
class finishbuilding(webapp2.RequestHandler):

	# standard variables
	sinfo = ''
	respn = ''
	error = ''
	debug = ''

	# get function implementation
	def get(self):
		# reset/clean standard variables
		Utils.reset(self)

		# validate and assign parameters
		passwd = Utils.required(self, 'passwd')
		version = config.data_version['building']
		if self.request.get('version'):
			version = self.request.get('version')
		lang = config.server["defaultLanguage"]
		if self.request.get('lang'):
			lang = self.request.get('lang')
		uuid = Utils.required(self, 'uuid')
		inid = Utils.required(self, 'inid')

		# start count
		start_time = time.time()

		# set default parameters
		player = None
		buildings = None
		mybuilding = None
		economy = None


		# if error, skip this
		if self.error == '':
			player = Player.getplayer(self, uuid)

		# if error or player is not, then skip to the end
		if self.error == '' and player is not None:
			buildings = Data.getbuildings(self, lang, version)

		if self.error == '' and buildings is not None:
			mybuilding = Building.getmybuilding(self, uuid, inid)

		# if any error or mybuilding is none, then skip to the end
		if self.error == '' and mybuilding is not None:
			if mybuilding.status != Building.BuildingStatus.PENDING:
				self.respn = '{"warning":"building='+inid+' has been finished."}'
			else:
				economy = Data.getDataAsObj(self, 'economy', config.data_version['economy'])

		if self.error == '' and self.respn == '' and economy is not None:
			_upd = False
			time_left = buildings.as_obj[mybuilding.itid][mybuilding.level-1]['build_time'] - int((start_time - mybuilding.timestamp)/60)
			if mybuilding.status == Building.BuildingStatus.PENDING:
				if time_left > 0:
					sele = economy.obj[0]
					for list in economy.obj:
						if time_left >= list['time_in_minutes']:
							sele = list
						else:
							break

					if player.state_obj['gold'] >= sele['gold_value']:
						player.state_obj['gold'] -= sele['gold_value']
						mybuilding.status = Building.BuildingStatus.DELIVERED
						_upd = True

						player.info_obj['updated'] = start_time
						Player.setplayer(self, player)
					else:
						self.respn = '{"warning":"not enough gold!"}'
				else:
					mybuilding.status = Building.BuildingStatus.DELIVERED
					_upd = True

			if _upd is True:
				Building.setmybuilding(self, mybuilding)

			if self.error == '' and self.respn == '':
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