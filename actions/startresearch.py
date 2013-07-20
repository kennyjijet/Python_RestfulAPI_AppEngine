""" startresearch action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae


	Description
	---------------------------------------------------------------
	I am an API to add research to player


	Input:
	---------------------------------------------------------------
	required: passwd, uuid, itid
	optional: lang, version,


	Output:
	---------------------------------------------------------------
	An added research info

"""

# built-in libraries
import webapp2
import logging
import time
import json

# google's libraries
from google.appengine.ext import db

# config
from config import config

# include
from helpers.utils import Utils
from models.Data import Data
from models.Item import Item
from models.Player import Player
#from models.Building import Building
from models.Research import Research

# class implementation
class startresearch(webapp2.RequestHandler):

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
		uuid = Utils.required(self, 'uuid')
		itid = Utils.required(self, 'itid')

		# check password
		if self.error == '' and passwd != config.testing['passwd']:
			self.error = 'passwd is incorrect.'

		start_time = time.time()												# start count

		# logical variables
		player = None
		researches = None
		research = None

		# if error, skip this
		if self.error == '':
			player = Player.getplayer_as_obj(self, uuid)

		if self.error == '' and player is not None:
			researches = Data.getresearches(self, float(version))

		if self.error == '' and researches is not None:
			_name = str(itid)
			_pos = itid.find('.', len(itid)-4)
			_bui = itid[0:_pos]
			_lev = itid[_pos+1:len(itid)]

			try:
				research = researches.as_obj[_bui][_lev]
			except KeyError:
				self.error = itid + " was not found!"

		if self.error == '' and research is not None:
			add = True
			if player.state_obj['cash'] < research['cost'] and self.respn == '':
				self.respn = '{"warning":"not enough cash!"}'
			if player.state_obj['fuel'] < research['fuel'] and self.respn == '':
				self.respn = '{"warning":"not enough fuel!"}'
			if player.state_obj['tire'] < research['tire'] and self.respn == '':
				self.respn = '{"warning":"not enough tire!"}'
			if player.state_obj['battery'] < research['battery'] and self.respn == '':
				self.respn = '{"warning":"not enough battery!"}'
			if player.state_obj['oil'] < research['oil'] and self.respn == '':
				self.respn = '{"warning":"not enough oil!"}'
			if player.state_obj['brake'] < research['brake'] and self.respn == '':
				self.respn = '{"warning":"not enough brake!"}'

		if self.respn == '' and self.error == '':
			player.state_obj['cash'] -= research['cost']
			player.state_obj['fuel'] -= research['fuel']
			player.state_obj['tire'] -= research['tire']
			player.state_obj['battery'] -= research['battery']
			player.state_obj['oil'] -= research['oil']
			player.state_obj['brake'] -= research['brake']
			if Player.setplayer_as_obj(self, player):
				myresearch = Research.newresearch(self)
				myresearch.uuid = uuid
				myresearch.itid = itid
				myresearch.inid = Utils.genanyid(self, 'r')
				myresearch.status = Research.ResearchStatus.PENDING
				myresearch.timestamp = int(start_time)
				Research.setmyresearch(self, myresearch)
				self.respn = '{"state":'+player.state+','
				self.respn += '"researches":['
				self.respn = Research.compose_myresearch(self.respn, myresearch)
				self.respn = self.respn.rstrip(',') + ']'
				self.respn += '}'

		# calculate time taken and return the result
		time_taken = time.time() - start_time
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))

	# do exactly as get() does
	def post(self):
		self.get()