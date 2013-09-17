""" getdata action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae


	Description
	---------------------------------------------------------------
	I am an API to get game data(s) (Data deployed from Google Drive
	Custom Backend


	Input:
	---------------------------------------------------------------
	required: passwd, type,
	optional: version, lang


	Output:
	---------------------------------------------------------------
	requested game data(s)


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
class ping(webapp2.RequestHandler):

	# standard variables
	sinfo = ''
	respn = ''
	error = ''
	debug = ''

	# get function implementation
	def get(self):
		self.respn = '"removed replay -> score code. changed":"Cast [created] to string, delayed cron for 1st",' \
                     '"version":"1"}'
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, 1))

	# do exactly as get() does
	def post(self):
		self.get()