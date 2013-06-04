""" loadplayer action class

	Project: GrandCentral-GAE API
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae
	

	Description
	---------------------------------------------------------------
	I am an API to get user's list of items

	
	Input:
	---------------------------------------------------------------
	required: uuid
	optional:

	
	Output:
	---------------------------------------------------------------
	list of user's items 
	
"""

# built-in libraries
import webapp2
import json
import logging
import time

# google's libraries
from google.appengine.api import memcache

# config
from config import config

# include
from helpers.utils import Utils
from models.Player import Player
from models.Data import Data
from models.Item import Item

# class implementation
class getmyitems(webapp2.RequestHandler):
	# standard variables
	sinfo = ''
	respn = ''
	error = ''
	debug = ''

	# get function implementation
	def get(self):
		Utils.reset(self)                                                        # reset/clean standard variables

		# validate and assign parameters
		uuid = Utils.required(self, 'uuid')

		start_time = time.time()                                                # start count

		# if error, skip this
		if self.error == '':
			player = Player.getplayer_as_obj(self, uuid)                        # get player state

		# if error or player is none, then skip to the end
		if self.error == '' and player is not None:
			storeitem = Data.getstoreitem_as_obj(self, config.softstore['version'])    # get store item
			items = None                                                        # set items as none
			if storeitem is not None:                                            # if storeitem is none, everything just done here, will skip to the end
				items = Item.getitems(self, uuid)                                # get all items that belongs to this uuid
			if items is not None:
				change = 0
				self.respn = '{'
				for item in items:
					if storeitem[str(item.itid)]:

						# update item's status -> for more detail see softpurchase.py
						save = False
						if item.status == 'pending' and int(start_time) >= item.timestamp:
							item.status = 'reward'
							item.timestamp = int(start_time) + storeitem[item.itid]['produce_time']
							save = True
						elif item.status == 'reward':
							item.status = 'rewarded'
							save = True

						if storeitem[item.itid]['resource_units'] >= 0:
							if item.status == 'reward' or item.status == 'rewarded':
								if int(start_time) >= item.timestamp:
									item.status = 'produced'
									save = True

						# compose list of items to return
						self.respn += '"' + item.inid + '":{'
						self.respn += '"itid"		: "' + item.itid + '",'
						self.respn += '"type"		: "' + storeitem[item.itid]['type'] + '",'
						self.respn += '"title"		: "' + storeitem[item.itid]['title'] + '",'
						self.respn += '"desc"		: "' + storeitem[item.itid]['description'] + '",'
						self.respn += '"imgurl"		: "' + storeitem[item.itid]['image_url_sd'] + '",'
						self.respn += '"data"		: "' + item.userData + '",'
						self.respn += '"status"		: "' + item.status + '",'
						self.respn += '"timestamp"	: ' + str(item.timestamp)
						self.respn += '},'

						if save is True:
							item.put()

				self.respn = self.respn.rstrip(',') + '}'

				if change > 0:
					memcache.delete(config.db['itemdb_name'] + '.' + str(uuid))
					if not memcache.add(config.db['itemdb_name'] + '.' + str(uuid), items, config.memcache['holdtime']):
						logging.warning('Core - Memcache set items failed')

		# calculate time taken and return result
		time_taken = time.time() - start_time
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))

	# do exactly as get() does
	def post(self):
		self.get()
