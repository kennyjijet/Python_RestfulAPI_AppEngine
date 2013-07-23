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
from models.Car import Car
from models.Challenge import Challenge

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
		guid = self.request.get('guid')
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
		total_wins = 0
		advice_checklist = ''

		player = None
		defaultitems = None

		if self.error == '' and passwd != config.testing['passwd']:                	# if password is incorrect
			self.error = 'passwd is incorrect.'                                    	# inform user via error message

		start_time = time.time()                                                	# start count

		# if error, skip this
		if self.error == '' and fbid != '':
			player = Player.getplayerByFbid(self, fbid)

		if player is None and uuid != '':
			player = Player.getplayer(self, uuid)                        			# get player from Player model class helper, specified by uuid

		defaultitems = Data.getDataAsObj(self, 'defaultitems', config.data_version['defaultitems'])
		if defaultitems is not None:

			if player is None:                                                    	# if no player data returned or doesn't exist
				#####################################################################################################################
				## Create new player data
				player = Player(parent=db.Key.from_path('Player', config.db['playerdb_name']))    # create a new player state data
				uuid = Utils.genanyid(self, 'u')
				if fbid == '':
					fbid = uuid
				player.uuid = uuid                        							# assign uuid
				player.fbid = fbid
				# and assign all player info and state
				player.info_obj = {'uuid': player.uuid, 'fbid': player.fbid, 'token': token, 'name': name, 'photo': photo, 'lang': lang}
				player.state_obj = {'guid': guid, 'cash': cash, 'gold': gold, 'current_car':'', 'total_wins': total_wins, 'advice_checklist': advice_checklist, 'updated': start_time}

				#####################################################################################################################
				## Init default item for new player
				buildings = Data.getbuildings(self, lang, float(version))
				cars = Data.getcars(self, lang, float(version))
				upgrades = Data.getupgrades(self, lang, float(version))

				if buildings is not None and cars is not None and upgrades is not None:

					for item in defaultitems.obj:
						if item['type'] == 'state':
							player.state_obj[item['id']] = item['value']
						elif item['type'] == 'building':
							try:
								building = buildings.as_obj[item['id']][0]
								if building is not None:
									if player.state_obj['cash'] >= building['cost']:
										player.state_obj['cash'] -= building['cost']
										mybuilding = Building.newbuilding(self)
										mybuilding.uuid = player.uuid
										mybuilding.itid = item['id']
										mybuilding.inid = Utils.genanyid(self, 'b')
										mybuilding.level = building['level']
										mybuilding.status = Building.BuildingStatus.PENDING
										mybuilding.location = item['value']
										mybuilding.timestamp = int(start_time)
										Building.setmybuilding(self, mybuilding)
							except KeyError:
								logging.warning('KeyError, key not found!')

						elif item['type'] == 'car':
							type = ''
							car = None
							for _car in cars.as_obj:
								if _car['id'] == item['id']:
									car = _car
									break
							if player.state_obj['cash'] >= car['cost']:
								player.state_obj['cash'] -= car['cost']
								mycar = Car.create(self, player.uuid)
								mycar.data_obj['info'] = {'crid': car['id']}
								mycar.data_obj['upgrades'] = []
								mycar.data_obj['equip'] = {}
								player.state_obj['current_car'] = mycar.cuid
								default_upgrades = car['default_upgrades'].replace(' ', '').split(',')
								for default_upgrade in default_upgrades:
									mycar.data_obj['upgrades'].append(default_upgrade)
									for _type in upgrades.as_obj:
										try:
											mycar.data_obj['equip'][type]
										except KeyError:
											for upgrade in upgrades.as_obj[_type]:
												if upgrade['id'] == default_upgrade:
													mycar.data_obj['equip'][_type] = default_upgrade
													break
													break
								Car.update(self, mycar)

			else:                                                                	# but if player does exist
				#####################################################################################################################
				## Found existing user
				uuid = player.uuid
				if token:                                                        	# if token is provided
					player.state_obj['token'] = token                            	# assign token to player state
				if fbid != '':
					player.fbid = fbid
					player.info_obj['fbid'] = fbid
					player.info_obj['photo'] = photo                                	# assign photo url
				player.info_obj['name'] = name                                    	# assign name
				try:
					updated = player.state_obj['updated']
				except KeyError:
					player.state_obj['updated'] = start_time
				if self.request.get('lang'):
					player.info_obj['lang'] = lang

				try:
					if guid:
						player.state_obj['guid'] = guid
				except KeyError:
					player.state_obj['guid'] = ''

				# try .. cash and assign new property
				try:
					cash = player.state_obj['cash']
				except KeyError:
					player.state_obj['cash'] = cash
				try:
					total_wins = player.state_obj['total_wins']
				except KeyError:
					player.state_obj['total_wins'] = total_wins
				try:
					advice_checklist = player.state_obj['advice_checklist']
				except KeyError:
					player.state_obj['advice_checklist'] = advice_checklist

			if Player.setplayer(self, player):                            # write down to database
				self.error = ''                                                    # then obviously, no error
				type = ''
				for item in config.playerdata:
					type += item+','
				type = type.rstrip(',')
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
					elif item == 'car':
						mycars = Car.list(self, player.uuid)
						self.respn += '"car":['
						for _car in mycars:
							self.respn += Car.compose_mycar('', _car) + ','
						self.respn = self.respn.rstrip(',') + '],'
					elif item == 'challenge':
						self.respn += '"challenge":{"challengers":['
						challengers = Challenge.GetChallengers(self, player.fbid)
						if challengers is not None:
							for _challenge in challengers:
								_gameObj = json.loads(_challenge.data)
								self.respn += '{'
								self.respn += '"chid":"'+_challenge.id+'",'
								self.respn += '"uidx":"'+_challenge.uid1+'",'
								self.respn += '"track":"'+_challenge.track+'",'
								self.respn += '"lapTime":'+str(_gameObj['player1']['lapTime'])+','
								self.respn += '"created":"'+_gameObj['player1']['created']+'"'
								self.respn += '},'
						self.respn = self.respn.rstrip(',') + '],"challenging":['
						challenging = Challenge.GetChallenging(self, player.fbid)
						if challenging is not None:
							for _challenge in challenging:
								_gameObj = json.loads(_challenge.data)
								self.respn += '{'
								self.respn += '"chid":"'+_challenge.id+'",'
								self.respn += '"uidx":"'+_challenge.uid2+'",'
								self.respn += '"track":"'+_challenge.track+'",'
								self.respn += '"lapTime":'+str(_gameObj['player2']['lapTime'])+','
								self.respn += '"created":"'+_gameObj['player2']['created']+'"'
								self.respn += '},'
						self.respn = self.respn.rstrip(',') + '],"completed":['
						completed = Challenge.GetCompleted(self, player.fbid)
						if completed is not None:
							for _challenge in completed:
								_gameObj = json.loads(_challenge.data)
								self.respn += '{'
								self.respn += '"chid":"'+_challenge.id+'",'
								if player.fbid == _challenge.uid1:
									self.respn += '"uidx":"'+_challenge.uid2+'",'
								else:
									self.respn += '"uidx":"'+_challenge.uid1+'",'
								self.respn += '"track":"'+_challenge.track+'",'
								self.respn += '"lapTime":'+str(_gameObj['player2']['lapTime'])+','
								self.respn += '"created":"'+_gameObj['player2']['created']+'"'
								self.respn += '},'
						self.respn = self.respn.rstrip(',') + ']},'
				self.respn = self.respn.rstrip(',') + '}'

			else:                                                                # but if write down to database was failed
				self.error = 'unable to insert/update player data.'                # inform user bia error message

		# calculate time taken and return the result
		time_taken = time.time() - start_time
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))

	# do exactly as get() does
	def post(self):
		self.get()