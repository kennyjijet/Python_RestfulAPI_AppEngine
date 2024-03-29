""" getmybuildings action class

    Project: GrandCentral-GAE
    Author: Plus Pingya
    Github: https://github.com/Gamepunks/grandcentral-gae


    Description
    ---------------------------------------------------------------
    I am an API to get list of buildings owned by player


    Input:
    ---------------------------------------------------------------
    required: passwd, uuid
    optional: lang, version


    Output:
    ---------------------------------------------------------------
    list of buildings

"""

# built-in libraries
import webapp2
import logging
import time
import json

# config
from config import config

# include
from helpers.utils import Utils
from models.Data import Data
from models.Item import Item
from models.Player import Player
from models.Building import Building

# class implementation
class getmybuildings(webapp2.RequestHandler):

    # standard variables
    game = ''
    sinfo = ''
    respn = ''
    error = ''
    debug = ''

    # get function implementation
    def get(self):
        Utils.reset(self)														# reset/clean standard variables

        # validate and assign parameters
        passwd = Utils.required(self, 'passwd')
        version = config.data_version['building']
        if self.request.get('version'):
            version = self.request.get('version')
        lang = config.server["defaultLanguage"]
        if self.request.get('lang'):
            lang = self.request.get('lang')
        uuid = Utils.required(self, 'uuid')
        guid = self.request.get('guid')

        # check password
        if self.error == '' and passwd != config.testing['passwd']:
            self.error = 'passwd is incorrect.'

        start_time = time.time()												# start count

        # logical variables
        player = None
        buildings = None
        mybuildings = None

        # if error, skip this
        if self.error == '':
            player = Player.getplayer(self, uuid)

        if self.error == '' and player is not None and guid != '':
            if guid != player.state_obj['guid']:
                player = None
                self.error = config.error_message['dup_login']

        if self.error == '' and player is not None:
            buildings = Data.getbuildings(self, lang, version)

        if self.error == '' and buildings is not None:
            mybuildings = Building.getmybuildings(self, uuid)

        if self.error == '' and mybuildings is not None:
            self.respn = '['
            for mybuilding in mybuildings:
                # update building status, determine production
                _upd = False
                if mybuilding.status == Building.BuildingStatus.PENDING:
                    if mybuilding.timestamp + (buildings.as_obj[mybuilding.itid][mybuilding.level-1]['build_time']*60) <= start_time:
                        mybuilding.timestamp = int(start_time)
                        mybuilding.status = Building.BuildingStatus.DELIVERED
                        _upd = True
                elif mybuilding.status == Building.BuildingStatus.DELIVERED:
                    mybuilding.status = Building.BuildingStatus.OWNED
                    _upd = True
                if _upd is True:
                    Building.setmybuilding(self, mybuilding)
                self.respn = Building.compose_mybuilding(self.respn, mybuilding)
            self.respn = self.respn.rstrip(',') + ']'

            # update timestamp for player
            player.state_obj['updated'] = start_time
            Player.setplayer(self, player)

        # calculate time taken and return the result
        time_taken = time.time() - start_time
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(Utils.RESTreturn(self, time_taken))

    # do exactly as get() does
    def post(self):
        self.get()