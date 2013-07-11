""" deleteplayer action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae
	

	Description
	---------------------------------------------------------------
	I am an API to delete player account, this includes
	player state, scores, items, record

	
	Input:
	---------------------------------------------------------------
	required: passwd, uuid
	optional: 

	
	Output:
	---------------------------------------------------------------
	result success or failed
	
"""

# build-in libraries
import webapp2
import logging
import time

# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache

# config
from config			import config

# include
from models.Player 	import Player
from models.Score 	import Score
from models.Item	import Item
from models.Record  import Record
from models.Building import Building
from models.Challenge import Challenge
from helpers.utils		import Utils

# class implementation
class deleteplayer(webapp2.RequestHandler):

    # standard variables
	sinfo = ''
	respn = ''
	error = ''
	debug = ''

	# get function implementation
	def get(self):
		Utils.reset(self)                                               # reset/clean standard variables

		# validate and assign parameters
		passwd	= Utils.required(self, 'passwd')
		uuid	= Utils.required(self, 'uuid')

		# check password
		if self.error == '' and passwd != config.testing['passwd']:
			self.error = 'passwd is incorrect.'

		start_time = time.time()                                        # start count

		# if error, skip this
		if self.error == '':

			# query player state for given uuid
			players = Player.all().filter('uuid =', uuid).ancestor(db.Key.from_path('Player', config.db['playerdb_name'])).fetch(1)
			didDelete = False                                           # we have not delete anything yet
			for player in players:                                      # we might have duplicate data, just delete them all

				# query scores for this player and delete them all
				scores = Score.all().filter('uuid =', player.uuid).ancestor(db.Key.from_path('Score', config.db['scoredb_name']))
				for score in scores:
					score.delete()

				# query items for this player and delete them all
				items = Item.all().filter('uuid =', player.uuid).ancestor(db.Key.from_path('Item', config.db['itemdb_name']))
				for item in items:
					item.delete()

				# query records for this player and delete them all
				records = Record.all().filter('uuid =', player.uuid).ancestor(db.Key.from_path('Record', config.db['recorddb_name']))
				for record in records:
					record.delete()

				# query buildings for this player and delete them all
				buildings = Building.all().filter('uuid =', player.uuid).ancestor(db.Key.from_path('Building', config.db['buildingdb_name']))
				for building in buildings:
					building.delete()

				# delete all this user's challenge
				Challenge.DeleteByUserId(self, player.fbid)

				# and finally, delete this player
				player.delete()
				didDelete = True

			# compose result
			if didDelete == True:
				self.respn =  '"'+uuid+' was deleted successfully."'
			else:
				self.error = uuid+' does not exist in Database.'

		# calculate time taken and return the result
		time_taken =  time.time() - start_time
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))

	# do exactly as get() does
	def post(self):
		self.get()