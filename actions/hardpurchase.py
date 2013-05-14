""" hardpurchase action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae
	

	Description
	---------------------------------------------------------------
	I am an API to make purchase for hard item (platinum) 
	from Apple In-App Purchase. I will need receipt from client
	api to set to Apple Service to validation the transaction.

	
	Input:
	---------------------------------------------------------------
	required: uuid, itid, receipt
	optional: 

	
	Output:
	---------------------------------------------------------------
	player uuid and entire player state
	
"""

# built-in libraries
import webapp2
import json
import logging
import math
import time
import base64
import urllib2
import hashlib
from random 		import randint
from datetime 		import datetime, date

# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache, urlfetch

# config
from config			import config

# include
from helpers.utils		import Utils
#from models.Storeitem 	import Storeitem
from models.Data		import Data
from models.Player		import Player
from models.Record		import Record

# class implementation
class hardpurchase(webapp2.RequestHandler):
	
	# standard variables
	sinfo = ''
	respn = ''
	error = ''
	debug = ''
		
	# get function implementation
	def get(self):
		Utils.reset(self)															# reset/clean standard variables
		
		# validate and assign parameters
		uuid	= Utils.required(self, 'uuid')
		itid 	= Utils.required(self, 'itid')
		receipt = Utils.required(self, 'receipt')
		start_time = time.time()													# start count 
		
		# if error, skip this
		if self.error == '':
			player = Player.getplayer_as_obj(self, uuid)							# get player state
		
		# if error or player is none, then skip to the end
		if self.error == '' and player is not None:	
			record = Record.getrecord(self, uuid, itid, receipt)					# get record, get existing one or create new
					
		# if error or record is none, then skip this to the end
		if self.error == '' and record is not None:
			# select the apple verifying receipt url (live or sandbox)
			if config.apple['sandbox']==True: 							
				url = config.apple['verifyingReceiptSandboxURL']
			else:
				url = config.apple['verifyingReceiptURL']
			# now we do send out verification to apple service with our receipt data
			result = urlfetch.fetch(url=url,
						payload='{"receipt-data":"'+receipt+'"}',
						method=urlfetch.POST,
						headers={'Content-Type': 'text/json; charset=utf-8'},
						validate_certificate=False)

			if result.status_code == 200 or receipt==config.apple['testReceipt']:	# check if we've got a complete response from Apple Service
				resultobj = json.loads(result.content)								# if yes, parse result into json object, so we can read it
				if resultobj['status']==0 or receipt==config.apple['testReceipt']:	# if response's status is 0, this means our receipt is valid
					storeitem = Data.getstoreitem_as_obj(self)					# get store item, so we know what to reward/deliver
					item = None
					if storeitem is not None:
						try:
							item = storeitem[resultobj['receipt']['product_id']]	# pick purchased item
						except KeyError:
							if receipt == config.apple['testReceipt']:
								item = storeitem[config.apple['testItemId']]
					if item is not None:											# if everything is ready
						player.state_obj['platinum'] += item['platinum']			# add up platinum to player
						if Player.setplayer_as_obj(self, player):					# update player database
							record.status = 'rewarded'								# change status of item record to 'rewarded'	
							if Record.setrecord(self, record):						# update this record	
								Player.compose_player(self, player)					# compose result
					else:															# if purchased item info couldn't be found
						self.error = 'Item couldn\'t be found in the current shop\'s version' # then tell them
						
				else:																# if apple's response's status is not 0, that means something went wrong
					self.error = 'transaction reciept is invalid #code '+str(resultobj['status'])				# then tell them
					record.status = str(resultobj['status'])						# mark error code in status
					Record.setrecord(self, record)									# and update
					
		# calculate time taken and return result
		time_taken =  time.time() - start_time;
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))
		
	# do exactly as get() does
	def post(self):
		self.get()