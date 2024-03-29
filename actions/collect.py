""" collect action class

    Project: GrandCentral-GAE
    Author: Plus Pingya
    Github: https://github.com/Gamepunks/grandcentral-gae


    Description
    ---------------------------------------------------------------
    I am an API to collect resource produced from building


    Input:
    ---------------------------------------------------------------
    required: passwd, uuid, inid, amount
    optional: version


    Output:
    ---------------------------------------------------------------
    updated with added resource player state, and collected building info

"""

# built-in libraries
import time

import webapp2
import logging

# config
from config import config

# include
from helpers.utils import Utils
from models.Data import Data
from models.Player import Player
from models.Building import Building

from GCVars import GCVars

# class implementation
class collect(webapp2.RequestHandler):
    # standard variables
    game = ''
    sinfo = ''
    respn = ''
    error = ''
    debug = ''
    action = 'collect'

    # get function implementation
    def get(self):
        Utils.reset(self)                                                        # reset/clean standard variables

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
        amount = Utils.required(self, 'amount')

        # check password
        if self.error == '' and passwd != config.testing['passwd']:
            self.error = 'passwd is incorrect.'

        Utils.LogRequest(self)

        start_time = time.time()                                                # start count

        # logic variables
        player = None
        buildings = None
        mybuilding = None
        res_produced = 0

        # if error, skip this
        if self.error == '':
            player = Player.getplayer(self, uuid)
        """
        if self.error == '' and player is not None and guid != '':
            if guid != player.state_obj['guid']:
                player = None
                self.error = config.error_message['dup_login']
        """
        if self.error == '' and player is not None:
            buildings = Data.getbuildings(self, lang, version)

        if self.error == '' and buildings is not None:
            mybuilding = Building.getmybuilding(self, uuid, inid)

        if self.error == '' and mybuilding is not None:
            _upd = False
            if mybuilding.status == Building.BuildingStatus.PENDING:
                if mybuilding.timestamp + (
                        buildings.as_obj[mybuilding.itid][mybuilding.level - 1]['build_time'] * 60) <= start_time:
                    mybuilding.timestamp = int(start_time)
                    mybuilding.status = Building.BuildingStatus.DELIVERED
                    _upd = True
            elif mybuilding.status == Building.BuildingStatus.DELIVERED:
                mybuilding.status = Building.BuildingStatus.OWNED
                _upd = True

            if mybuilding.status == Building.BuildingStatus.DELIVERED or mybuilding.status == Building.BuildingStatus.OWNED:
                time_delta = (start_time - mybuilding.timestamp) / 60
                if time_delta > buildings.as_obj[mybuilding.itid][mybuilding.level - 1]['resource_interval'] > 0:
                    #mybuilding.status = Building.BuildingStatus.PRODUCED_PARTIAL
                    #_upd = True
                    res_produced = int(
                        time_delta / buildings.as_obj[mybuilding.itid][mybuilding.level - 1]['resource_interval']) * buildings.as_obj[mybuilding.itid][mybuilding.level - 1]['resource_produced']
                    if res_produced >= buildings.as_obj[mybuilding.itid][mybuilding.level - 1]['resource_capacity']:
                        res_produced = buildings.as_obj[mybuilding.itid][mybuilding.level - 1]['resource_capacity']
                        ##mybuilding.status = Building.BuildingStatus.PRODUCED
                        #_upd = True
            elif mybuilding.status == Building.BuildingStatus.PRODUCED_PARTIAL or mybuilding.status == Building.BuildingStatus.PRODUCED:
                if mybuilding.amount is None:
                    mybuilding.amount = 0;
                res_produced = mybuilding.amount
                mybuilding.amount = 0
                mybuilding.status = Building.BuildingStatus.OWNED
                _upd = True

            if res_produced > 0:
                if res_produced > amount:
                    res_produced = amount
                try:
                    # eg player['cash'] += 1
                    resource_type = buildings.as_obj[mybuilding.itid][mybuilding.level - 1]['resource']
                    _upd = True
                    new_amount = int(res_produced) + int(mybuilding.amount)
                    logging.debug('resource to collect = ' + str(res_produced) + " " + str(resource_type) + " = " + str(new_amount))
                    logging.debug('building contains = ' + str(res_produced))

                    player.state_obj[
                        buildings.as_obj[mybuilding.itid][mybuilding.level - 1]['resource']] += new_amount
                    # update timestamp for player
                    player.state_obj['updated'] = start_time
                    if Player.setplayer(self, player):
                        #mybuilding.status = Building.BuildingStatus.OWNED
                        mybuilding.timestamp = int(start_time)
                        _upd = True
                except KeyError:
                    self.error = 'resource=' + buildings.as_obj[mybuilding.itid][mybuilding.level - 1][
                        'resource'] + ' doesn\'t exist in player properties!'

            if _upd is True:
                Building.setmybuilding(self, mybuilding)

            if self.error == '':
                self.respn = '{"state":' + player.state + ', "building":['
                self.respn = Building.compose_mybuilding(self.respn, mybuilding)
                self.respn = self.respn.rstrip(',') + ']'
                self.respn += '}'

        # calculate time taken and return the result
        time_taken = time.time() - start_time
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(Utils.RESTreturn(self, time_taken))

    # do exactly as get() does
    def post(self):
        self.get()
