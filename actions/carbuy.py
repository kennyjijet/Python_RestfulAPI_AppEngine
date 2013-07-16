""" carbuy action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae


	Description
	---------------------------------------------------------------
	I am an API to get buy and obtain car


	Input:
	---------------------------------------------------------------
	required: passwd, uuid, crid
	optional: lang, version


	Output:
	---------------------------------------------------------------
	obtained car

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
from models.Data import Data
from models.Player import Player
from models.Car import Car

# class implementation
class carbuy(webapp2.RequestHandler):

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
		crid = Utils.required(self, 'crid')

		# check password
		if self.error == '' and passwd != config.testing['passwd']:
			self.error = 'passwd is incorrect.'

		start_time = time.time()												# start count

		# logical variables
		player = None
		cars = None
		car = None
		mycars = None

		# if error, skip this
		if self.error == '':
			player = Player.getplayer(self, uuid)

		if self.error == '' and player is not None:
			cars = Data.getcars(self, lang, float(version))

		if self.error == '' and cars is not None:
			found = False
			for _car in cars.as_obj:
				if _car['id'] == crid:
					car = _car
					found = True
					break
			if found is False:
				self.error = crid + " was not found!"

		if self.error == '' and car is not None:
			mycars = Car.list(self, uuid)
			for _car in mycars:
				info_obj = json.loads(_car.info)
				if info_obj['crid'] == crid:
					car = None
					self.respn = '{"warning":"You have already purchased this car."}'
					break

		if self.error == '' and car is not None:
			if player.state_obj['cash'] >= car['cost']:
				player.state_obj['cash'] -= car['cost']
				player.info_obj['updated'] = start_time 						# update timestamp for player
				if Player.setplayer(self, player):
					mycar = Car.create(self, player.uuid)
					mycar.info_obj['crid'] = car['id']
					upgrades = car['default_upgrades'].replace(' ', '').split(',')
					for upgrade in upgrades:
						mycar.upgrades_obj.append({"upgrade":upgrade,"used":True})
					if Car.update(self, mycar):
						self.respn = '{"state":'+player.state+','
						self.respn += '"car":['
						self.respn = Car.compose_mycar(self.respn, mycar)
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