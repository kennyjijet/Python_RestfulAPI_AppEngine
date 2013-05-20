""" testing action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae


	Description
	---------------------------------------------------------------
	I am an API to do all test


	Input:
	---------------------------------------------------------------
	required: passwd
	optional:


	Output:
	---------------------------------------------------------------
	result


"""

# built-in libraries
import webapp2
import logging
import time
import json

# google's libraries
from google.appengine.api import urlfetch

# config
from config import config

# include
from helpers.utils import Utils
import GrandCentral

from actions.saveplayer import saveplayer

# class implementation
class testing(webapp2.RequestHandler):

    # standard variables
    sinfo = ''
    respn = ''
    error = ''
    debug = ''

    logarr = None

    # get function implementation
    def get(self):
        Utils.reset(self)                                                        # reset/clean standard variables

        self.logarr = []

        # validate and assign parameters
        passwd = Utils.required(self, 'passwd')

        # check password
        if self.error == '' and passwd != config.testing['passwd']:
            self.error = 'passwd is incorrect.'

        start_time = time.time()                                                # start count

        # if error, skip this
        if self.error == '':

            # saveplayer
            request = webapp2.Request.blank(
                '/saveplayer?passwd=' + passwd + '&name=testPlus Pingya&photo=http://graph.facebook.com/pluspingya/picture?type=large')
            response = request.get_response(GrandCentral.app)
            response_obj = json.loads(response.body);
            self.error = response_obj['error']
        if self.error == '':
            uuid = response_obj['response']['uuid']
            self.log('saveplayer -> ' + uuid + " created")
            self.log(response_obj['response'])

            # getsoftstore
            request = webapp2.Request.blank('/getsoftstore?uuid=' + uuid)
            response = request.get_response(GrandCentral.app)
            response_obj = json.loads(response.body);
            self.error = response_obj['error']
        if self.error == '':
            num = len(response_obj['response'])
            self.log('getsoftstore -> ' + str(num) + ' items were found from softstore')
            self.log(response_obj['response'])

            # softpurchase - not qualified to purchase
            request = webapp2.Request.blank('/softpurchase?uuid=' + uuid + '&itid=Car.3')
            response = request.get_response(GrandCentral.app)
            response_obj = json.loads(response.body);
            self.error = response_obj['error']
        if self.error == '':
            res = response_obj['response']['warning']
            self.log('softpurchase(Car.3) -> ')
            self.log(response_obj['response'])

            # softpurchase - success
            request = webapp2.Request.blank('/softpurchase?uuid=' + uuid + '&itid=Car.1')
            response = request.get_response(GrandCentral.app)
            response_obj = json.loads(response.body);
            self.error = response_obj['error']
        if self.error == '':
            for i in response_obj['response']['items']:
                inid = i
            self.log('softpurchase(Car.1) -> ' + inid + ' has been purchased')
            self.log(response_obj['response'])

            # softpurchase - reach the maximum
            request = webapp2.Request.blank('/softpurchase?uuid=' + uuid + '&itid=Car.1')
            response = request.get_response(GrandCentral.app)
            response_obj = json.loads(response.body);
            self.error = response_obj['error']
        if self.error == '':
            res = response_obj['response']['warning']
            self.log('softpurchase(Car.1) -> ')
            self.log(response_obj['response'])

            # hardpurchase
            request = webapp2.Request.blank('/hardpurchase?uuid='+uuid+'&itid=Platinum.1&receipt='+config.apple['testReceipt'])
            response = request.get_response(GrandCentral.app)
            response_obj = json.loads(response.body);
            self.error = response_obj['error']
        if self.error == '':
            self.log('hardpurchase -> ')
            self.log(response_obj['response'])

            # softpurchase - not enough gold
            request = webapp2.Request.blank('/softpurchase?uuid='+uuid+'&itid=Car.2')
            response = request.get_response(GrandCentral.app)
            response_obj = json.loads(response.body);
            self.error = response_obj['error']
        if self.error == '':
            self.log('softpurchase(Car.2) -> ')
            self.log(response_obj['response'])

            # setpntoken
            request = webapp2.Request.blank('/setpntoken?passwd='+passwd+'&uuid='+uuid+'&token=testpntoken')
            response = request.get_response(GrandCentral.app)
            response_obj = json.loads(response.body);
            self.error = response_obj['error']
        if self.error == '':
            self.log('testpntoken -> device token has been set')
            self.log(response_obj['response'])

            # finish now
            request = webapp2.Request.blank('/finishnow?uuid='+uuid+'&inid='+inid)
            response = request.get_response(GrandCentral.app)
            response_obj = json.loads(response.body);
            self.error = response_obj['error']
        if self.error == '':
            self.log('finishnow -> the given item should be rewarded now')
            self.log(response_obj['response'])

            # loadplayer
            request = webapp2.Request.blank('/loadplayer?uuid='+uuid)
            response = request.get_response(GrandCentral.app)
            response_obj = json.loads(response.body);
            self.error = response_obj['error']
        if self.error == '':
            self.log('loadplayer -> ')
            self.log(response_obj['response'])

            # getmyitems
            request = webapp2.Request.blank('/getmyitems?uuid='+uuid)
            response = request.get_response(GrandCentral.app)
            response_obj = json.loads(response.body);
            self.error = response_obj['error']
        if self.error == '':
            self.log('getmyitems -> ')
            self.log(response_obj['response'])

            #deleteplayer
            request = webapp2.Request.blank('/deleteplayer?passwd='+passwd+'&uuid='+uuid)
            response = request.get_response(GrandCentral.app)
            response_obj = json.loads(response.body);
            self.error = response_obj['error']
        if self.error == '':
            self.log('deleteplayer -> ' + uuid + " deleted")
            self.log(response_obj['response'])

            #getdata (advisdor)
            request = webapp2.Request.blank('/getdata?passwd='+passwd+'&type=advisor&version=1')
            response = request.get_response(GrandCentral.app)
            response_obj = json.loads(response.body);
            self.error = response_obj['error']
        if self.error == '':
            self.log('getdata(advisor) ->')
            self.log(response_obj['response'])

            self.respn = json.dumps(self.logarr)

        # calculate time taken and return the result
        time_taken =  time.time() - start_time
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(Utils.RESTreturn(self, time_taken))

    # do exactly as get() does
    def post(self):
        self.get()

    def log(self, txt):
        logging.info(txt)
        self.logarr.append(txt)
