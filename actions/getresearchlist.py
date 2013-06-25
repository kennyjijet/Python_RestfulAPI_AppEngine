""" getresearchlist action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae


	Description
	---------------------------------------------------------------
	I am an API to get list of researches that user can do


	Input:
	---------------------------------------------------------------
	required: passwd,
	optional: lang, version


	Output:
	---------------------------------------------------------------
	list of researches

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

# class implementation
class getresearchlist(webapp2.RequestHandler):

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
		version = config.data_version['research']
		if self.request.get('version'):
			version = self.request.get('version')
		lang = config.server["defaultLanguage"]
		if self.request.get('lang'):
			lang = self.request.get('lang')

		# check password
		if self.error == '' and passwd != config.testing['passwd']:
			self.error = 'passwd is incorrect.'

		start_time = time.time()												# start count

		# logical variables
		researches = None

		# if error, skip this
		if self.error == '':
			researches = Data.getresearches(self, lang, float(version))

		if self.error == '' and researches is not None:
			self.respn = '['
			for research in researches.as_obj:
				logging.info(research)
				self.respn += json.dumps(researches.as_obj[research][0])+','
			self.respn = self.respn.rstrip(',') + ']'


		# calculate time taken and return the result
		time_taken = time.time() - start_time
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))

	# do exactly as get() does
	def post(self):
		self.get()