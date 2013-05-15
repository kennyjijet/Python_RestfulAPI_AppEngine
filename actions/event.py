""" event action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae


	Description
	---------------------------------------------------------------
	I am an API to trig event for all events in the game


	Input:
	---------------------------------------------------------------
	required: passwd, uuid, evid
	optional:


	Output:
	---------------------------------------------------------------
	depends on events, most of them returns player state


"""

# built-in libraries
import webapp2
import logging
import time

# config
from config         import config

# include
from helpers.utils  import Utils
from models.Data    import Data
from models.Item    import Item
from models.Player  import Player

# behaviour class implementation
class behaviour():

    @staticmethod
    def reward(self, prms):
        player = None
        params = prms.split(',')                                                # parameters came in commas separate value format
        if len(params) != 3:                                                    # check if we have exact number of parameters
            self.error = 'Reward event received invalid parameter(s)! example: uuid #,resource,@amount'
        else:
            self.error = ''
            player = Player.getplayer_as_obj(self, params[0])
        if self.error == '' and player is not None:
            player.state_obj[params[1]] += int(params[2])                       # add up / reward
            Player.setplayer_as_obj(self, player)
            Player.compose_player(self, player)

    @staticmethod
    def deduct(self, prms):
        player = None
        params = prms.split(',')                                                # parameters came in commas separate value format
        if len(params) != 3:                                                    # check if we have exact number of parameters
            self.error = 'Deduct event receieved invalid parameter(s)! example: uuid #,resource,@amount'
        else:
            self.error = ''
            player = Player.getplayer_as_obj(self, params[0])
        if self.error == '' and player is not None:
            player.state_obj[params[1]] -= int(params[2])                       # deduct
            Player.setplayer_as_obj(self, player)
            Player.compose_player(self, player)

    @staticmethod
    def collect(self, prms):
        player = None
        item = None
        params = prms.split(',')                                                # parameters came in commas separate value format
        if len(params) != 4:                                                    # check if we have exact number of parameters
            self.error = 'Collect event receieved invalid parameter(s)! eg: uuid,itid'
        else:
            self.error = ''
            player = Player.getplayer_as_obj(self, params[0])
            item = Item.getspecificinidproduceditem(self, params[0], params[1])
        if player is not None and item is not None:
            storeitem = Data.getstoreitem_as_obj(self)
            if len(storeitem) >= 1:
                player.state_obj[params[3]] += int(storeitem[item.itid]['resource_units'])
                item.status = 'rewarded'
                item.timestamp = time.time() + storeitem[item.itid]['produce_time']
                if item.put():
                    Player.setplayer_as_obj(self, player)
                    Player.compose_player(self, player)
                else:
                    self.error = 'event: unable to update item!'
        else:
            self.respn = '{"warning":"no item has resource produced!"}'

# class implementation
class event(webapp2.RequestHandler):

    # standard variables
    sinfo = ''
    respn = ''
    error = ''
    debug = ''

    # get function implementation
    def get(self):
        Utils.reset(self)														# reset/clean standard variables

        # validate and assign parameters
        passwd = Utils.required(self, 'passwd')
        evid = Utils.required(self, 'evid')
        prms = Utils.required(self, 'prms')

        # check password
        if self.error == '' and passwd != config.testing['passwd']:
            self.error = 'passwd is incorrect.'

        start_time = time.time()												# start count

        # if error, skip this
        if self.error == '':

            # try to find event data for given event
            events = Data.getevents_as_obj(self)
            self.error = 'event ' + evid + ' does not exist!'
            if events is not None:
                for event in events:                                            # there are more than one behavior for one event
                    if event == evid:                                           # so we need to behave all of them
                        # add parameters
                        params = prms                                           # assign user parameters
                        for item in events[event]:                                      # and add event data parameter
                            if "parameter" in str(item) and events[event][item] != '':
                                params += ',' + str(events[event][item])
                        getattr(behaviour, events[event]['behaviour'])(self, params)    # call behavior class to behave the event

        # calculate time taken and return the result
		time_taken =  time.time() - start_time
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))

	# do exactly as get() does
	def post(self):
		self.get()