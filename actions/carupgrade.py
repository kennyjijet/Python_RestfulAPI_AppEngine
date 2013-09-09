""" carupgrade action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae


	Description
	---------------------------------------------------------------
	I am an API to buy upgrade and equip it to the car,
	or just equip it to the car if you're already have that upgrade

	Input:
	---------------------------------------------------------------
	required: passwd, uuid, cuid, upid
	optional: lang, version


	Output:
	---------------------------------------------------------------
	car info with all upgrades

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
from models.Building import Building
from models.Car import Car

# class implementation
class carupgrade(webapp2.RequestHandler):

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
		guid = self.request.get('guid')
		cuid = Utils.required(self, 'cuid')
		upid = Utils.required(self, 'upid')

		# check password
		if self.error == '' and passwd != config.testing['passwd']:
			self.error = 'passwd is incorrect.'

		start_time = time.time()												# start count

		# logical variables
		player = None
		upgrades = None
		upgrade = None
		mycar = None
		qualify = False

		# if error, skip this
		if self.error == '':
			player = Player.getplayer(self, uuid)

		if self.error == '' and player is not None and guid != '':
			if guid != player.state_obj['guid']:
				player = None
				self.error = config.error_message['dup_login']

		if self.error == '' and player is not None:
			mycar = Car.get(self, cuid)

		if self.error == '' and mycar is not None:
			upgrades = Data.getupgrades(self, lang, version)

		if self.error == '' and upgrades is not None:
			found = False
			for _type in upgrades.as_obj:
				for _upgrade in upgrades.as_obj[_type]:
					if _upgrade['id'] == upid:
						upgrade = _upgrade
						found = True
						break
			if found is False:
				self.error = 'Upgrade id='+upid+' was not found.'

		if self.error == '' and upgrade is not None:

			# validate existing upgrade
			already_have = False
			for _upgrade in mycar.data_obj['upgrades']:
				if _upgrade == upid:
					already_have = True

			# validate building
			buildings = Building.list(self, player.uuid)
			for building in buildings:
				if building.itid == upgrade['shop'] and building.level >= upgrade['shop_level']:
					qualify = True
					break
			if qualify is False:
				self.respn = '{"warning":"Player does not have required building to buy upgrade."}'

		if self.error == '' and qualify is True:
			# validate cash
			if already_have is False: 												# then you need to buy it, dude!
				if player.state_obj['cash'] >= upgrade['cost']:
					player.state_obj['cash'] -= upgrade['cost']
					player.state_obj['updated'] = start_time
					if Player.setplayer(self, player):
						mycar.data_obj['upgrades'].append(upgrade['id'])
				else:
					self.respn = '{"warning":"not enough cash!"}'
					qualify = False

		if self.error == '' and qualify is True:
			mycar.data_obj['equip'][upgrade['type']] = upgrade['id']
			if Car.update(self, mycar):
				self.respn = '{"state":'+player.state+','
				self.respn += '"car":['
				self.respn += Car.compose_mycar('', mycar) + ','
				self.respn = self.respn.rstrip(',') + ']'
				self.respn += '}'

		# calculate time taken and return the result
		time_taken = time.time() - start_time
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))

	# do exactly as get() does
	def post(self):
		self.get()