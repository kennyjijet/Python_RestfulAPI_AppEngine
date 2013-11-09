""" getmyresearches action class

    Project: GrandCentral-GAE
    Author: Plus Pingya
    Github: https://github.com/Gamepunks/grandcentral-gae


    Description
    ---------------------------------------------------------------
    I am an API to get list of researches owned by player


    Input:
    ---------------------------------------------------------------
    required: passwd, uuid
    optional: lang, version


    Output:
    ---------------------------------------------------------------
    list of player's researches

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
from models.Research import Research

# class implementation
class getmyresearches(webapp2.RequestHandler):

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
        version = config.data_version['buildings']
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
        researches = None
        myresearches = None

        # if error, skip this
        if self.error == '':
            player = Player.getplayer_as_obj(self, uuid)

        if self.error == '' and player is not None and guid != '':
            if guid != player.state_obj['guid']:
                player = None
                self.error = config.error_message['dup_login']

        if self.error == '' and player is not None:
            researches = Data.getresearches(self, version)

        if self.error == '' and researches is not None:
            myresearches = Research.getmyresearches(self, uuid)

        if self.error == '' and myresearches is not None:
            self.respn = '['
            for myresearch in myresearches:
                # update building status, determine production
                _name = str(myresearch.itid)
                _pos = myresearch.itid.find('.', len(myresearch.itid)-4)
                _bui = myresearch.itid[0:_pos]
                _lev = myresearch.itid[_pos+1:len(myresearch.itid)]
                _upd = False
                if myresearch.status == Research.ResearchStatus.PENDING:
                    if myresearch.timestamp + (researches.as_obj[_bui][_lev]['wait']*60) <= start_time:
                        myresearch.timestamp = int(start_time)
                        myresearch.status = Research.ResearchStatus.REWARD
                        _upd = True
                elif myresearch.status == Research.ResearchStatus.REWARD:
                    myresearch.status = Research.ResearchStatus.OWNED
                    _upd = True
                if _upd is True:
                    Research.setmyresearch(self, myresearch)
                self.respn = Research.compose_myresearch(self.respn, myresearch)
            self.respn = self.respn.rstrip(',') + ']'

        # calculate time taken and return the result
        time_taken = time.time() - start_time
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(Utils.RESTreturn(self, time_taken))

    # do exactly as get() does
    def post(self):
        self.get()