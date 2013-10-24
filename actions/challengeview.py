""" challengeview action class

    Project: GrandCentral-GAE
    Author: Plus Pingya
    Github: https://github.com/Gamepunks/grandcentral-gae


    Description
    ---------------------------------------------------------------
    I am an API to get a challenge


    Input:
    ---------------------------------------------------------------
    required: passwd, uuid, chid
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

# class implementation
class challengeview(webapp2.RequestHandler):

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
        chid = Utils.required(self, 'chid')

        # check password
        if self.error == '' and passwd != config.testing['passwd']:
            self.error = 'passwd is incorrect.'

        start_time = time.time()												# start count

        Utils.LogRequest(self)
        # logic variables
        player = None

        # if error, skip this
        if self.error == '':
            player = Player.getplayer(self, uuid)

        if self.error == '' and player is not None and guid != '':
            if guid != player.state_obj['guid']:
                player = None
                self.error = config.error_message['dup_login']

        if self.error == '' and player is not None:
            challenge = Challenge.GetChallenge(self, chid)
            if challenge is not None:
                if player.fbid == challenge.uid1 or player.fbid == challenge.uid2 or player.uuid == challenge.uid1 or player.uuid == challenge.uid2:
                    self.respn = '{'
                    Challenge.ComposeActualChallenge(self, challenge)
                    self.respn = self.respn.rstrip(',') + '}'
                else:
                    self.error = 'You don\'t have permission to access data of this challenge.'

            # update timestamp for player
            player.state_obj['updated'] = start_time
            Player.setplayer(self, player)

        # calculate time taken and return the result
        time_taken = time.time() - start_time
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(Utils.RESTreturn(self, time_taken,False))

    # do exactly as get() does
    def post(self):
        self.get()