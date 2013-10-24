""" getsoftstore action class

    Project: GrandCentral-GAE
    Author: Plus Pingya
    Github: https://github.com/Gamepunks/grandcentral-gae


    Description
    ---------------------------------------------------------------
    I am an API to get list of  all items in store, and also
    evaluate user by uuid, are they eligible to buy


    Input:
    ---------------------------------------------------------------
    required: uuid
    optional:


    Output:
    ---------------------------------------------------------------
    List of all items in store


"""

# built-in libraries
import webapp2
import json
import logging
import time

# config
from config				import config

# include
from helpers.utils		import Utils
from models.Player 		import Player
from models.Data		import Data
from models.Item		import Item

# class implementation
class getsoftstore(webapp2.RequestHandler):

    # standard variables
    sinfo = ''
    respn = ''
    error = ''
    debug = ''

    # get function implementation
    def get(self):
        Utils.reset(self)											# reset/clean standard variables

        # validate and assign parameters
        uuid = Utils.required(self, 'uuid')
        guid = self.request.get('guid')
        start_time = time.time()									# start count

        # if error, skip this
        if self.error == '':
            player = Player.getplayer_as_obj(self, uuid)			# get player state from Player model class helper

        if self.error == '' and player is not None and guid != '':
            if guid != player.state_obj['guid']:
                player = None
                self.error = config.error_message['dup_login']

        # if error or player is none, skip this
        if self.error == '' and player is not None:
            storeitem = Data.getstoreitem_as_arr(self)		# get store item from Storeitem model class helper

        # if error or storeitem is none, skip this
        if self.error == '' and storeitem is not None:
            myitems = Item.getitems(self, uuid)						# get list of items owned

            # set result default
            self.respn = '['
            reason = ''

            for item in storeitem:									# run through each item in store items

                add = True											# A variable indicates that is it available for user
                if item['dependencies'] != '':						# if item has dependencies
                    add = False										# set item to unavailable first, we will change it available after we check all its dependencies
                    reason = 'You need the following items first: ' + item['dependencies']; # also inform user some good reason, not just die. this will eliminate after we check all its dependencies anyway
                    depc = 0										# A variable stand from dependencies counter
                    deps = item['dependencies'].replace(' ', '').split(',')	# and eliminate space from dependencies and split by commas ','
                    for dep in deps:								# run through all dependences of the item
                        for myitem in myitems:						# run through all user's list of items
                            if myitem.itid == dep:					# check if user have dependency item
                                depc = depc + 1						# increment counter
                    if depc >= len(deps):							# alter all counting, if counter is more than all dependecies, it probably means user has all dependencies
                        add = True									# and then yeah!, we turn item to available

                if add == True and item['maximum'] != '':			# check if the item has maximum limitation
                    depc = 0										# set counter to 0 again, we will use for next logic
                    for myitem in myitems:							# run through myitems
                        if myitem.itid == item['id']:				# check if user has same item in hand
                            depc = depc + 1							# increment counter
                    if int(depc) >= int(item['maximum']):			# if counter is more than or equal the item's maximum
                        add = False									# that means user has reached the maximum, and should not available for him any more
                        reason = 'You\'ve reached the maximum of this item!' # and yes! should inform him that

                # hard compose item list
                self.respn += '{'
                self.respn += ' "itid":"'+item['id']+'",'
                self.respn += ' "type":"'+item['type']+'",'
                self.respn += ' "title":"'+item['title']+'",'
                self.respn += ' "desc":"'+item['description']+'",'
                self.respn += ' "depend":"'+item['dependencies']+'",'
                self.respn += ' "imgurl":"'+item['image_url_sd']+'",'
                self.respn += ' "gold":'+str(item['gold'])+','
                self.respn += ' "time":'+str(item['time'])+','
                self.respn += ' "platinum":'+str(item['platinum'])+','
                if add == True:
                    self.respn += ' "lock":""'
                else:
                    self.respn += ' "lock":"'+reason+'"'
                self.respn += '},'

            self.respn = self.respn.rstrip(',') + ']'

        # calculate time taken and return result
        time_taken = time.time() - start_time
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(Utils.RESTreturn(self, time_taken))

    # do exactly as get() does
    def post(self):
        self.get()