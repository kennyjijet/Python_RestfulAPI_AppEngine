""" getuitext action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae

	Description
	---------------------------------------------------------------
	I am an API to get UI text data by given language code (Data deployed from Google Drive

	Input:
	---------------------------------------------------------------
	required: passwd, lang,
	optional: version

	Output:
	---------------------------------------------------------------
	requested language data

"""

# built-in libraries
import webapp2
import logging
import time
import json

# google's libraries
from google.appengine.api import memcache

# config
from config import config

# include
from helpers.utils import Utils
from models.Data import Data

# class implementation
class getuitext(webapp2.RequestHandler):

	# standard variables
	sinfo = ''
	respn = ''
	error = ''
	debug = ''

	# get function implementation
	def get(self):
		Utils.reset(self)                                                        # reset/clean standard variables

		# validate and assign parameters
		passwd = Utils.required(self, 'passwd')
		lang = Utils.required(self, 'lang')
		version = self.request.get('version')
		if version is None or version == '':
			version = config.dictionary['version']

		# check password
		if self.error == '' and passwd != config.testing['passwd']:
			self.error = 'passwd is incorrect.'

		start_time = time.time()                                                # start count

		# if error, skip this
		if self.error == '':
			data = Data.gettransui(self, float(version))
			if data is not None:
				try:
					self.respn = json.dumps(data.as_obj[lang])
				except KeyError:
					self.error = 'UI Text for give language was not found!'

		# calculate time taken and return the result
		time_taken = time.time() - start_time
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))

	# do exactly as get() does
	def post(self):
		self.get()