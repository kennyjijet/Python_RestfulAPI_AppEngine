""" getplayerbasicdatas action class

    Project: GrandCentral-GAE
    Author: Plus Pingya
    Github: https://github.com/Gamepunks/grandcentral-gae


    Description
    ---------------------------------------------------------------
    I am an API to get the array of basic player data.
    update, total_winds


    Input:
    ---------------------------------------------------------------
    required: passwd, uuid, fbids = list of friend's fbid, separate by commas
    optional:


    Output:
    ---------------------------------------------------------------
    Array of basic plater data

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
from models.Challenge import Challenge

# class implementation
class getplayerbasicdatas(webapp2.RequestHandler):
    # standard variables
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
        fbids = Utils.required(self, 'fbids')

        if self.error == '' and passwd != config.testing['passwd']:                    # if password is incorrect
            self.error = 'passwd is incorrect.'                                        # inform user via error message

        start_time = time.time()                                                # start count

        # if error, skip this
        if self.error == '':
            player = Player.getplayer(self,
                                      uuid)                                # get player state from Player helper class, specified by uuid

        if self.error == '' and player is not None and guid != '':
            if guid != player.state_obj['guid']:
                player = None
                self.error = config.error_message['dup_login']

        if self.error == '' and player is not None:                                                # if have some data returned
            self.respn = '['
            _fbids = fbids.split(',')
            for fbid in _fbids:
                _friend = Player.getplayerByFbid(self, fbid)

                if _friend is None:
                    _friend = Player.getplayer(self, fbid)

                if _friend is not None:
                    _upd = False
                    self.respn += '{"fbid":"' + fbid + '",'
                    try:
                        self.respn += '"total_wins":' + str(_friend.state_obj['total_wins']) + ','
                    except KeyError:
                        self.respn += '"total_wins":0,'
                        _friend.state_obj['total_wins'] = 0
                        _upd = True
                    try:
                        self.respn += '"updated":' + str(_friend.info_obj['updated']) + '},'
                    except KeyError:
                        self.respn += '"updated":' + str(start_time) + '},'
                        _friend.info_obj['updated'] = start_time
                        _upd = True

                    if _upd is True:
                        Player.setplayer(self, _friend)

            self.respn = self.respn.rstrip(',') + ']'
            self.error = ''

            player.state_obj['updated'] = start_time
            Player.setplayer(self, player)

        # calculate time taken and return result
        time_taken = time.time() - start_time
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(Utils.RESTreturn(self, time_taken))

    # do exactly as get() does
    def post(self):
        self.get()