""" getplayerdata action class

    Project: GrandCentral-GAE
    Author: Plus Pingya
    Github: https://github.com/Gamepunks/grandcentral-gae


    Description
    ---------------------------------------------------------------
    I am an API to get player data, inventory, or both optionally.


    Input:
    ---------------------------------------------------------------
    required: passwd, uuid, type = list of data, separate by commas
    optional: specific


    Output:
    ---------------------------------------------------------------
    player data, inventory, or both

"""

# built-in libraries
import webapp2
import json
import logging
import time

# config
from config import config

# include
from helpers.utils import Utils
from models.Data import Data
from models.Player import Player
from models.Building import Building
from models.Car import Car
from models.Challenge import Challenge

# class implementation
class getplayerdata(webapp2.RequestHandler):

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
        uuid = Utils.required(self, 'uuid')
        guid = self.request.get('guid')
        type = Utils.required(self, 'type')
        version = config.data_version['building']
        if self.request.get('version'):
            version = self.request.get('version')
        lang = config.server["defaultLanguage"]
        if self.request.get('lang'):
            lang = self.request.get('lang')

        if self.error == '' and passwd != config.testing['passwd']:                	# if password is incorrect
            self.error = 'passwd is incorrect.'                                    	# inform user via error message
        Utils.LogRequest(self)
        start_time = time.time()                                                # start count

        # if error, skip this
        if self.error == '':
            player = Player.getplayer(self, uuid)								# get player state from Player helper class, specified by uuid

        if self.error == '' and player is not None and guid != '':
            if guid != player.state_obj['guid']:
                player = None
                self.error = config.error_message['dup_login']

        if self.error == '' and player is not None:												# if have some data returned
            self.respn = '{'
            if type == 'all':
                type = ''
                for item in config.playerdata:
                    type += item+','
                type = type.rstrip(',')
            types = type.split(',')
            for item in types:
                if item == 'info':
                    self.respn += '"info":'+player.info+','
                elif item == 'state':
                    self.respn += '"state":'+player.state+','
                elif item == 'building':
                    buildings = Data.getbuildings(self, lang, version)
                    mybuildings = Building.getmybuildings(self, uuid)
                    if buildings is not None and mybuildings is not None:
                        self.respn += '"building":['
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
                        self.respn = self.respn.rstrip(',') + '],'
                elif item == 'car':
                    mycars = Car.list(self, uuid)
                    if mycars is not None:
                        self.respn += '"car":['
                        for _car in mycars:
                            self.respn += Car.compose_mycar('', _car) + ','
                        self.respn = self.respn.rstrip(',') + '],'
                elif item == 'challenge':
                    Challenge.ComposeChallenges(self, player)

            self.respn = self.respn.rstrip(',') + '}'

        # calculate time taken and return result
        time_taken = time.time() - start_time
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(Utils.RESTreturn(self, time_taken))

    # do exactly as get() does
    def post(self):
        self.get()