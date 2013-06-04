""" collect action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae


	Description
	---------------------------------------------------------------
	I am an API to collect resource produced by building


	Input:
	---------------------------------------------------------------
	required: passwd, uuid, inid
	optional:


	Output:
	---------------------------------------------------------------


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
from models.Item import Item
from models.Player import Player

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
		uuid = Utils.required(self, 'uuid')
		inid = Utils.required(self, 'inid')

		# check password
		if self.error == '' and passwd != config.testing['passwd']:
			self.error = 'passwd is incorrect.'

		start_time = time.time()												# start count

		# if error, skip this
		if self.error == '':

			player = Player.getplayer_as_obj(self, uuid)
			if self.error == '' and player is not None:
				storeitems = Data.getstoreitem_as_obj(self)

			if self.error == '' and storeitems is not None:
				item = Item.getitembyinid(self, uuid, inid)
				if item is None:
					self.error = 'Item='+inid+' couldn\'t be found!'

			if self.error == '' and item.status != 'produced':
				self.error = "Resource was not produced!"

			if self.error == '' and player.uuid != item.uuid:
				self.error = "item="+inid+" is not belong to player="+uuid

			if self.error == '':
				self.respn = storeitems[item.itid]['resource']
				#self.respn = "OK"
				#player.state_obj[]

		# calculate time taken and return the result
		time_taken = time.time() - start_time
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))

	# do exactly as get() does
	def post(self):
		self.get()