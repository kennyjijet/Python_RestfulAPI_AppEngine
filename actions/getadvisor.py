""" getadvisor action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae


	Description
	---------------------------------------------------------------
	I am an API to get advisor data (Data deployed from Google Drive)

	Input:
	---------------------------------------------------------------
	required: passwd,
	optional:

	Output:
	---------------------------------------------------------------
	advisor data

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

# class implementation
class getadvisor(webapp2.RequestHandler):

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

		# check password
		if self.error == '' and passwd != config.testing['passwd']:
			self.error = 'passwd is incorrect.'

		start_time = time.time()												# start count

		# if error, skip this
		if self.error == '':
			data = Data.getData(self, 'advisor', config.data_version['advisor'])
			if data is not None:
				self.respn = data.data

		# calculate time taken and return the result
		time_taken = time.time() - start_time
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))

	# do exactly as get() does
	def post(self):
		self.get()