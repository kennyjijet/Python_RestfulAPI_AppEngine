""" getrecentplayerlist action class

    Project: GrandCentral-GAE
    Author: Plus Pingya
    Github: https://github.com/Gamepunks/grandcentral-gae


    Description
    ---------------------------------------------------------------
    I am an API to get list of recent player basic data


    Input:
    ---------------------------------------------------------------
    required: passwd, uuid
    optional:


    Output:
    ---------------------------------------------------------------
    I am an API to get list of recent player basic data

"""

# built-in libraries
import webapp2
import json
import logging
import time

from google.appengine.api import memcache

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
class getrecentplayerlist(webapp2.RequestHandler):

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
        uuid = Utils.required(self, 'uuid')
        guid = self.request.get('guid')
        showme = self.request.get('showme')

        if self.error == '' and passwd != config.testing['passwd']:                	# if password is incorrect
            self.error = 'passwd is incorrect.'                                    	# inform user via error message

        start_time = time.time()                                                # start count

        player = None
        recentplayerlist = None

        # if error, skip this
        if self.error == '':
            player = Player.getplayer(self, uuid)								# get player state from Player helper class, specified by uuid

        if self.error == '' and player is not None and guid != '':
            if guid != player.state_obj['guid']:
                player = None
                self.error = config.error_message['dup_login']

        if self.error == '' and player is not None:												# if have some data returned
            recentplayerlist = Data.GetRecentPlayerList(self)

        if self.error == '' and recentplayerlist is not None:
            _range = config.recentplayer['maxlist']
            if _range > len(recentplayerlist.obj):
                _range = len(recentplayerlist.obj)

            self.respn = '['
            if _range > 0:
                _size = config.recentplayer['numlist'];
                if _range < _size:
                    _size = _range
                random = Utils.GetRandomOfNumberInArray(self, _size, _range)
                for i in random:
                    recentplayer = recentplayerlist.obj[i]
                    if recentplayer['uuid'] != player.uuid or showme == 'true':
                        self.respn += '{"fbid":"'+recentplayer['fbid']+'",'
                        self.respn += '"uuid":"'+recentplayer['uuid']+'",'
                        self.respn += '"name":"'+recentplayer['name']+'",'
                        self.respn += '"image":"'+recentplayer['image']+'",'
                        self.respn += '"total_wins":'+str(recentplayer['total_wins'])+','
                        self.respn += '"updated":'+str(recentplayer['updated'])+'},'
            self.respn = self.respn.rstrip(',') + ']'

        # calculate time taken and return result
        time_taken = time.time() - start_time
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(Utils.RESTreturn(self, time_taken))

    # do exactly as get() does
    def post(self):
        self.get()