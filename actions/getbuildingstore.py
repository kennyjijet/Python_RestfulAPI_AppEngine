""" getbuildingstore action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae


	Description
	---------------------------------------------------------------
	I am an API to get list of buildings that user can buy


	Input:
	---------------------------------------------------------------
	required: passwd,
	optional: lang, version


	Output:
	---------------------------------------------------------------
	list of buildings

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
class getbuildingstore(webapp2.RequestHandler):

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
		#uuid = Utils.required(self, 'uuid')

		# check password
		if self.error == '' and passwd != config.testing['passwd']:
			self.error = 'passwd is incorrect.'

		start_time = time.time()												# start count

		# logical variables
		buildings = None

		# if error, skip this
		if self.error == '':
			buildings = Data.getbuildings(self, float(version))

		if self.error == '' and buildings is not None:

			self.respn = '['
			for building in buildings.as_obj:
				logging.info(building)
				self.respn += json.dumps(buildings.as_obj[building]['1'])+','
			self.respn = self.respn.rstrip(',') + ']'

			#self.respn = buildings.data;

		# calculate time taken and return the result
		time_taken = time.time() - start_time
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))

	# do exactly as get() does
	def post(self):
		self.get()