""" challengeupdate action class

    Project: GrandCentral-GAE
    Author: Plus Pingya
    Github: https://github.com/Gamepunks/grandcentral-gae


    Description
    ---------------------------------------------------------------
    I am an API to update a challenge


    Input:
    ---------------------------------------------------------------
    required: passwd, uuid, chid, type, cuid, laptime, replay
    optional:


    Output:
    ---------------------------------------------------------------
    challenge data

"""

# built-in libraries
import webapp2
import logging
import time

# config
from config import config

# include
from helpers.utils import Utils
from models.Player import Player
from models.Challenge import Challenge
from models.Building import Building

# class implementation
class challengeupdate(webapp2.RequestHandler):
    # standard variables
    game = ''
    sinfo = ''
    respn = ''
    error = ''
    debug = ''

    # get function implementation
    def get(self):
        Utils.reset(self)                                                        # reset/clean standard variables

        # validate and assign parameters
        passwd = Utils.required(self, 'passwd')
        uuid = Utils.required(self, 'uuid')
        guid = self.request.get('guid')
        chid = Utils.required(self, 'chid')
        type = Utils.required(self, 'type')
        laptime = Utils.required(self, 'laptime')
        replay = Utils.required(self, 'replay')
        events = Utils.required(self, 'events')
        cardata = Utils.required(self, 'cardata')
        name = Utils.required(self, 'name')
        image = Utils.required(self, 'image')

        version = config.data_version['building']
        if self.request.get('version'):
            version = self.request.get('version')
        lang = config.server["defaultLanguage"]
        if self.request.get('lang'):
            lang = self.request.get('lang')

        #logging.info("events " + events);
        # check password
        if self.error == '' and passwd != config.testing['passwd']:
            self.error = 'passwd is incorrect.'

        start_time = time.time()                                                # start count

        # logic variables
        player = None

        # if error, skip this
        if self.error == '':
            player = Player.getplayer(self, uuid)

        if self.error == '' and player is not None and guid != '':
            logging.warn("trying to create challenge with" + player.uuid)
            if guid != player.state_obj['guid']:
                player = None
                self.error = config.error_message['dup_login']

        if self.error == '' and player is not None:
            logging.warn("trying to create challenge with" + player.uuid)

            challenge, my_building = Challenge.Update(self, chid, type, uuid, laptime, replay, events, cardata, name,
                                         image, lang, version)
            if challenge is not None:
                self.respn = '{'
                Challenge.ComposeChallenges(self, player)
                if my_building is not None:
                    self.respn += ',"building":['
                    self.respn = Building.compose_mybuilding(self.respn, my_building)
                    self.respn = self.respn.rstrip(',') + ']'
                self.respn = self.respn.rstrip(',') + '}'

            # update timestamp for player - this is to update if needed
            if challenge.manual_update is True:
                player.state_obj['updated'] = start_time
                Player.setplayer(self, player)

        # calculate time taken and return the result
        time_taken = time.time() - start_time
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(Utils.RESTreturn(self, time_taken))

    # do exactly as get() does
    def post(self):
        self.get()