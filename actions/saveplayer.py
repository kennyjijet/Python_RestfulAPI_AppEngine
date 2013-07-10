""" saveplayer action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae
	

	Description
	---------------------------------------------------------------
	I am an API to set/save/update player state

	
	Input:
	---------------------------------------------------------------
	required: passwd,
	optional: uuid, fbid, name, photo, token, lang

	
	Output:
	---------------------------------------------------------------
	player uuid and entire player state
	
	
"""

# built-in libraries
import webapp2
import json
import logging
import time

# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache

# config
from config import config

# include
from helpers.utils import Utils
from models.Player import Player
from models.Data import Data
from models.Building import Building

# class implementation
class saveplayer(webapp2.RequestHandler):
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

		uuid = self.request.get('uuid')
		fbid = self.request.get('fbid')

		version = config.data_version['building']

		token = self.request.get('token')
		lang = config.server["defaultLanguage"]
		if self.request.get('lang'):
			lang = self.request.get('lang')
		name = 'Guest' #Utils.genanyid(self, 'Guest')
		if self.request.get('name'):
			name = self.request.get('name')
		photo = ''
		if fbid != '':
			photo = 'https://graph.facebook.com/'+fbid+'/picture?type=large'
		gold = 10
		cash = 50000
		fuel = 5
		tire = 5
		battery = 5
		oil = 5
		brake = 5
		advice_checklist = ''

		player = None

		if self.error == '' and passwd != config.testing['passwd']:                	# if password is incorrect
			self.error = 'passwd is incorrect.'                                    	# inform user via error message

		start_time = time.time()                                                	# start count

		# if error, skip this
		if self.error == '' and fbid != '':
			player = Player.getplayerByFbid(self, fbid)

		if player is None and uuid != '':
			player = Player.getplayer(self, uuid)                        			# get player from Player model class helper, specified by uuid

		if player is None:                                                    	# if no player data returned or doesn't exist
			player = Player(parent=db.Key.from_path('Player', config.db['playerdb_name']))    # create a new player state data
			uuid = Utils.genanyid(self, 'u')
			player.uuid = uuid                        							# assign uuid
			player.fbid = fbid
			# and assign all player info and state
			player.info_obj = {'uuid': player.uuid, 'fbid': player.fbid, 'token': token, 'name': name, 'photo': photo, 'lang': lang}
			player.state_obj = {'gold': gold, 'cash': cash, 'fuel': fuel, 'tire': tire, 'battery': battery, 'oil': oil, 'brake': brake, 'advice_checklist': advice_checklist}
		else:                                                                	# but if player does exist
			uuid = player.uuid
			if token:                                                        	# if token is provided
				player.state_obj['token'] = token                            	# assign token to player state
			if fbid != '':
				player.fbid = fbid
				player.info_obj['fbid'] = fbid
				player.info_obj['photo'] = photo                                	# assign photo url

			player.info_obj['name'] = name                                    	# assign name
			if self.request.get('lang'):
				player.info_obj['lang'] = lang
			# try .. cash and assign new property
			try:
				gold = player.state_obj['gold']
			except KeyError:
				player.state_obj['gold'] = gold
			try:
				cash = player.state_obj['cash']
			except KeyError:
				player.state_obj['cash'] = cash
			try:
				fuel = player.state_obj['fuel']
			except KeyError:
				player.state_obj['fuel'] = fuel
			try:
				tire = player.state_obj['tire']
			except KeyError:
				player.state_obj['tire'] = tire
			try:
				battery = player.state_obj['battery']
			except KeyError:
				player.state_obj['battery'] = battery
			try:
				oil = player.state_obj['oil']
			except KeyError:
				player.state_obj['oil'] = oil
			try:
				brake = player.state_obj['brake']
			except KeyError:
				player.state_obj['brake'] = brake
			try:
				advice_checklist = player.state_obj['advice_checklist']
			except KeyError:
				player.state_obj['advice_checklist'] = advice_checklist

		if Player.setplayer(self, player):                            # write down to database
			self.error = ''                                                    # then obviously, no error
			type = 'info,state,building'
			self.respn = '{"uuid":"'+uuid+'",'
			types = type.split(',')
			for item in types:
				if item == 'info':
					self.respn += '"info":'+player.info+','
				elif item == 'state':
					self.respn += '"state":'+player.state+','
				elif item == 'building':
					buildings = Data.getbuildings(self, lang, version)
					mybuildings = Building.getmybuildings(self, uuid)
					if buildings is not None and mybuildings is not None:
						self.respn += '"building":['
						for mybuilding in mybuildings:
							# update building status, determine production
							_upd = False
							if mybuilding.status == Building.BuildingStatus.PENDING:
								if mybuilding.timestamp + (buildings.as_obj[mybuilding.itid][mybuilding.level-1]['build_time']*60) <= start_time:
									mybuilding.timestamp = int(start_time)
									mybuilding.status = Building.BuildingStatus.DELIVERED
									_upd = True
							elif mybuilding.status == Building.BuildingStatus.DELIVERED:
								mybuilding.status = Building.BuildingStatus.OWNED
								_upd = True
							if _upd is True:
								Building.setmybuilding(self, mybuilding)
							self.respn = Building.compose_mybuilding(self.respn, mybuilding)
						self.respn = self.respn.rstrip(',') + '],'
			self.respn = self.respn.rstrip(',') + '}'

			#Player.compose_player(self, player)                                # compose the entire player state to return

		else:                                                                # but if write down to database was failed
			self.error = 'unable to insert/update player data.'                # inform user bia error message

		# calculate time taken and return the result
		time_taken = time.time() - start_time
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))

	# do exactly as get() does
	def post(self):
		self.get()