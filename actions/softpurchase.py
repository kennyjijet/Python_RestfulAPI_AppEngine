""" softpurchase action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae
	

	Description
	---------------------------------------------------------------
	I am an API to make purchase (virtual money transaction)
	and reward item to user

	
	Input:
	---------------------------------------------------------------
	required: uuid, itid
	optional: 

	
	Output:
	---------------------------------------------------------------
	Player state and list of same type of purchased item
	
	
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
# models
from models.Item import Item

# include
from helpers.utils import Utils
from helpers.apns import apns

from models.Player import Player
from models.Data import Data
from models.Item import Item

# class implementation
class softpurchase(webapp2.RequestHandler):
	# standard variables
	sinfo = ''
	respn = ''
	error = ''
	debug = ''

	# get function implementation
	def get(self):
		Utils.reset(self)                                        	# reset/clean standard variables

		# validate and assign parameters
		uuid = Utils.required(self, 'uuid')
		itid = Utils.required(self, 'itid')
		data = self.request.get('data')
		start_time = time.time()                                 	# start count

		# set variables default
		item = None
		player = None
		storeitem = None

		# if error, skip this
		if self.error == '':
			player = Player.getplayer_as_obj(self, uuid)

		# if error or player is none, skip this
		if self.error == '' and player is not None:
			storeitem = Data.getstoreitem_as_obj(self, config.softstore['version'])

		# if storeitem is not none
		if storeitem is not None:
			try:                                                    # try to get item with id=itid
				item = storeitem[str(itid)]
			except KeyError:                                        # if item with that id/key doesn't exist
				storeitem = None                                    # throw it to None
				self.error = 'given item id doesn\'t exist!'        # and inform user that

		# if error or storeitem is none, skip to the end // return
		if self.error == '' and storeitem is not None:

			myitems = Item.getitems(self, uuid)                    	# get all items user owned from Item model class helper

			add = True                                          	# this variable indicates is user eligible to purchase
			if item['dependencies'] != '':                          # check if the item has dependencies
				add = False                                         # set item to unavailable first, we will change it available after we check all its dependencies
				self.respn = '{"warning":"you\'re not qualified to purchase this item!"}' 	# also inform user some good reason, not just die. this will eliminate after we check all its dependencies anyway
				depc = 0                                                    				# A variable stand from dependencies counter
				deps = item['dependencies'].replace(' ', '').split(',')        				# and eliminate space from dependencies and split by commas ','
				for dep in deps:                                            				# run through all dependencies of the item
					for myitem in myitems:                                    				# run through all user's list of items
						if myitem.itid == dep:                                				# check if user have dependency item
							depc += 1                                        				# increment counter
				if depc >= len(deps):                                        				# alter all counting, if counter is more than all dependencies, it probably means user has all dependencies
					add = True                                                				# and then yeah!, we turn item to available

			if add is True and item['maximum'] != '':                        				# check if the item has maximum limitation
				depc = 0                                                   			 		# set counter to 0 again, we will use for next logic
				for myitem in myitems:                                        				# run through myitems
					if myitem.itid == item['id']:                           	 			# check if user has same item in hand
						depc += 1                                        					# increment counter
				if int(depc) >= int(item['maximum']):                        				# if counter is more than or equal the item's maximum
					add = False                                                				# that means user has reached the maximum, and should not available for him any more
					self.respn = '{"warning":"you\'ve reached maximum of this item!"}'    	# and yes! should inform him that

			# now if user is eligible to purchase this item, then do it
			if add is True:
				if player.state_obj['gold'] >= item['gold']:                				# check if user has gold enough to purchase
					player.state_obj['gold'] -= item['gold']                				# deduct gold from user by item price
					itemobj = Item(parent=db.Key.from_path('Item', config.db['itemdb_name']))    	# now create an item and reward/deliver to user
					itemobj.itid = item['id']                                				# assign an itemid.. to identiy item type
					itemobj.inid = Utils.genitemid(self)                    				# generate and assign unique inventory id,
					itemobj.uuid = player.uuid                                				# assign uuid, indicate who is the owner of this item
					itemobj.userData = ''
					if storeitem[itemobj.itid]['type'] == Item.ItemType.BUILDING:
						itemobj.userData = data
					itemobj.status = 'pending'                                				# assign status, probably this is pending
					itemobj.timestamp = time.time() + float(item['time'])        			# calculate time to deliver or reward, while status pending, user can't use it
					if itemobj.put():                                        				# put it into database
						if player.state_obj['token'] != '':                					# check if user already has token
							apns.add(player.state_obj['token'], storeitem[str(itemobj.itid)]['title'] + ' has been delivered to you!', itemobj.timestamp) # if so, set a push notofication to be sent
						if Player.setplayer_as_obj(self, player):            				# put player state back into the database
							myitems = Item.getspecificitems(self, uuid, item['id'])    		# get user items (only same type of purchased item), we want to list them all and return
							if myitems is not None:                            				# make sure we have everything ready
								self.respn = '{'
								for myitem in myitems:                        				# run through myitems
									if storeitem[str(myitem.itid)]:            				# check if item does exist

										save = False                                                                                     	# this variable indicates should we update user's item data
										if myitem.status == 'pending' and time.time() >= myitem.timestamp:                                  # if item status is pending and it is time to reward
											myitem.status = 'reward'                                                                        # then reward it, by changing item status
											myitem.timestamp = time.time() + storeitem[str(myitem.itid)]['produce_time']                    # calculate next time to produce resource
											save = True                                                                                     # cause we change item status, so we need to update database
										elif myitem.status == 'reward':                                                                     # if status is reward,
											myitem.status = 'rewarded'                                                                      # we should change it to rewarded, so system won't duplicate reward
											save = True                                                                                     # and again, save it any time we change something

										# now, compose list of same type of purchased item
										self.respn += '"' + myitem.inid + '":{'
										self.respn += '"itid"		: "' + myitem.itid + '",'
										self.respn += '"type"		: "' + storeitem[myitem.itid]['type'] + '",'
										self.respn += '"title"		: "' + storeitem[myitem.itid]['title'] + '",'
										self.respn += '"desc"		: "' + storeitem[myitem.itid]['description'] + '",'
										self.respn += '"imgurl"		: "' + storeitem[myitem.itid]['image_url_sd'] + '",'
										self.respn += '"data"		: "' + myitem.userData + '",'
										self.respn += '"status"		: "' + myitem.status + '",'
										self.respn += '"timestamp"	: ' + str(myitem.timestamp)
										self.respn += '},'

										if save is True:                                                                                    # now we should know, should we update item data
											myitem.put()                                                                                    # if yes, please do so

								self.respn = self.respn.rstrip(',') + '}'
							else:                                                                                                          	# if we can't get my item,
								self.respn = '{}'                                                                                           # then return emtpy object

							self.respn = '{"uuid":"' + player.uuid + '", "state":' + player.state + ', "items":' + self.respn + '}'         # compose final result

				else:                                                       	 				# if user has not enough gold
					self.respn = '{"warning":"not enough gold!"}'            					# then tell him

		# calculate time taken and return result
		time_taken = time.time() - start_time
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))

	# do exactly as get() does
	def post(self):
		self.get()