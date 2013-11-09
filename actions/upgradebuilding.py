""" upgradebuilding action class

    Project: GrandCentral-GAE
    Author: Plus Pingya
    Github: https://github.com/Gamepunks/grandcentral-gae


    Description
    ---------------------------------------------------------------
    I am an API to upgrade a given building to the next level


    Input:
    ---------------------------------------------------------------
    required: passwd, uuid, inid
    optional: lang, version,


    Output:
    ---------------------------------------------------------------
    list of buildings

"""

# built-in libraries
import webapp2
import logging
import time
import json

# google's libraries
from google.appengine.ext import db

# config
from config import config

# include
from helpers.utils import Utils
from models.Data import Data
from models.Item import Item
from models.Player import Player
from models.Building import Building

# class implementation
class upgradebuilding(webapp2.RequestHandler):

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
        version = config.data_version['building']
        if self.request.get('version'):
            version = self.request.get('version')
        lang = config.server["defaultLanguage"]
        if self.request.get('lang'):
            lang = self.request.get('lang')
        uuid = Utils.required(self, 'uuid')
        guid = self.request.get('guid')
        inid = Utils.required(self, 'inid')

        # check password
        if self.error == '' and passwd != config.testing['passwd']:
            self.error = 'passwd is incorrect.'

        start_time = time.time()												# start count

        # logical variables
        player = None
        buildings = None
        building = None
        mybuilding = None

        # if error, skip this
        if self.error == '':
            player = Player.getplayer(self, uuid)

        if self.error == '' and player is not None and guid != '':
            if guid != player.state_obj['guid']:
                player = None
                self.error = config.error_message['dup_login']

        if self.error == '' and player is not None:
            buildings = Data.getbuildings(self, lang, float(version))

        if self.error == '' and buildings is not None:
            mybuilding = Building.getmybuilding(self, uuid, inid)

        if self.error == '' and mybuilding is not None:
            if mybuilding.status != Building.BuildingStatus.PENDING:
                try:
                    if len(buildings.as_obj[mybuilding.itid]) > mybuilding.level:
                        building = buildings.as_obj[mybuilding.itid][mybuilding.level]
                    else:
                        self.error = 'Level '+str(mybuilding.level+1)+' of building='+mybuilding.itid+' does not exist!'
                except KeyError:
                    self.error = 'Building='+mybuilding.itid+' does not exist!'
            else:
                self.respn = '{"warning":"Building='+inid+' still under construction, cannot upgrade at the moment!"}'

        if self.error == '' and self.respn == '' and building is not None:
            self.respn = str(building['cost'])
            if player.state_obj['cash'] >= building['cost']:
                player.state_obj['cash'] -= building['cost']
                # update timestamp for player
                player.state_obj['updated'] = start_time
                if Player.setplayer(self, player):
                    mybuilding.itid = building['id']
                    mybuilding.status = Building.BuildingStatus.PENDING
                    mybuilding.level = building['level']
                    mybuilding.timestamp = int(start_time)
                    Building.setmybuilding(self, mybuilding)
                    self.respn = '{"state":'+player.state+','
                    self.respn += '"building":['
                    self.respn = Building.compose_mybuilding(self.respn, mybuilding)
                    self.respn = self.respn.rstrip(',') + ']'
                    self.respn += '}'
            else:
                self.respn = '{"warning":"not enough cash!"}'



        # calculate time taken and return the result
        time_taken = time.time() - start_time
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(Utils.RESTreturn(self, time_taken))

    # do exactly as get() does
    def post(self):
        self.get()