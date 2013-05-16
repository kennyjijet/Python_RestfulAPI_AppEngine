""" finishnow action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae


	Description
	---------------------------------------------------------------
	I am an API to fast track finish now rewarding/deliver item


	Input:
	---------------------------------------------------------------
	required: uuid, inid
	optional:


	Output:
	---------------------------------------------------------------
	Item data


"""

# built-in libraries
import webapp2
import logging
import time
import math

# include
from helpers.utils  import Utils
from models.Data    import Data
from models.Item    import Item
from models.Player  import Player

# class implementation
class finishnow(webapp2.RequestHandler):

    # standard variables
    sinfo = ''
    respn = ''
    error = ''
    debug = ''

    # get function implementation
    def get(self):
        # reset/clean standard variables
        Utils.reset(self)

        # validate and assign parameters
        uuid = Utils.required(self, 'uuid')
        inid = Utils.required(self, 'inid')

        # start count
        start_time = time.time()

        # set default parameters
        player = None
        item = None

        # if error, skip this
        if self.error == '':
            player = Player.getplayer_as_obj(self, uuid)

        # if error or player is not, then skip to the end
        if self.error == '' and player is not None:
            item = Item.getitembyinid(self, uuid, inid)

        # if any error or item is none, then skip to the end
        if self.error == '' and item is not None:
            self.respn = '{"warning":"item is already rewarded!"}'                                                          # set default response
            if item.status == 'pending':
                milisecs = item.timestamp - start_time                                                                      # find time left
                if milisecs > 0:                                                                                            # if still have to wait
                    minutes = math.ceil(milisecs/60)                                                                        # convert to minute
                    if player.state_obj['platinum'] < minutes:                                                              # check if player has enough platinum to perform finishnow!
                        self.respn = '{"warning":"not enough platinum!"}'                                                   # if no, then tell them
                    else:                                                                                                   # but if yes
                        try:
                            storeitem = Data.getstoreitem_as_obj(self)                                                      # we need storeitem first
                            if storeitem is not None:                                                                       # if everything is allright
                                if storeitem[str(item.itid)]:			                                                    # check if item does exist
                                    player.state_obj['platinum'] -= minutes                                                 # deduct player's platinum
                                    Player.setplayer_as_obj(self, player)                                                   # save player state
                                    item.status = 'reward'                                                                  # turn item's status to 'reward'
                                    item.timestamp = start_time + storeitem[str(item.itid)]['produce_time']					# calculate next time to produce resource
                                    # now, compose list of same type of purchased item
                                    self.respn  = '{"'+item.inid+'":{'
                                    self.respn += '"itid"		: "'+item.itid+'",'
                                    self.respn += '"type"		: "'+storeitem[str(item.itid)]['type']+'",'
                                    self.respn += '"title"		: "'+storeitem[str(item.itid)]['title']+'",'
                                    self.respn += '"desc"		: "'+storeitem[str(item.itid)]['description']+'",'
                                    self.respn += '"imgurl"		: "'+storeitem[str(item.itid)]['image_url_sd']+'",'
                                    self.respn += '"status"		: "'+item.status+'",'
                                    self.respn += '"timestamp"		: '+str(item.timestamp)
                                    self.respn += '}}'
                                    Item.setitem(self, item)
                        except KeyError:
                            self.respn = '{"warning":"This item may no longer available!"}'                                 # if key not found

        # calculate time taken and return the result
        time_taken =  time.time() - start_time
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(Utils.RESTreturn(self, time_taken))

    # do exactly as get() does
    def post(self):
        self.get()