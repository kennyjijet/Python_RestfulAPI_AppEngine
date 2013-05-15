""" sendnotifications action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae


	Description
	---------------------------------------------------------------
	I am an API to send a list of notifications to apple push
	notification via our php proxy
    I am usually being called by cron job, please see cron.yaml

	Input:
	---------------------------------------------------------------
	required:
	optional:


	Output:
	---------------------------------------------------------------
	response message from our proxy

"""

# built-in libraries
import webapp2
import json
import logging
import time

from google.appengine.api import urlfetch

# config
from config			import config

# include
from helpers.apns	import apns
from helpers.utils	import Utils

# class implementation
class sendnotifications(webapp2.RequestHandler):

	# standard variables
	sinfo = ''
	respn = ''
	error = ''
	debug = ''

	# get function implementation
	def get(self):
		Utils.reset(self)											# reset/clean standard variables

		start_time = time.time()									# start count
		self.respn = '{"info":"no notification!"}'                  # set default response of the action

		list = apns.get()                                           # get list of notifications to be sent
		parameter = '[]'                                            # set default blank list of notification
		if(list):                                                   # if any notification
			parameter = json.dumps(list);                           # then parse all of it to parameters as a list (array) of notification

		# send to proxy url, which will connect with apple push notification service via socket
		result = urlfetch.fetch(url=config.apns['proxyurl'],
				payload='{"data":'+parameter+', "time":'+str(start_time)+',"passwd":"'+config.testing['passwd']+'"}',
				method=urlfetch.POST,
				headers={'Content-Type': 'text/json; charset=utf-8'},
				validate_certificate=False)

		if result.status_code == 200:                               # if success request
			self.respn = result.content                             # return response message as result
				
		apns.clean()                                                # after all done, clean local list of notification
				
		logging.info(self.respn)                                    # also do log, so we can read in consle log

		# calculate time taken and return result
		time_taken =  time.time() - start_time;
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))

	# do exactly as get() does
	def post(self):
		self.get()