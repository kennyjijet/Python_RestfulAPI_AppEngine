""" challengecreate action class

    Project: GrandCentral-GAE
    Author: Plus Pingya
    Github: https://github.com/Gamepunks/grandcentral-gae


    Description
    ---------------------------------------------------------------
    I am an API to create a challenge


    Input:
    ---------------------------------------------------------------
    required: passwd, uuid, track, toid
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
from models.Data import Data
from models.Player import Player
from models.Challenge import Challenge

# class implementation
class challengecreate(webapp2.RequestHandler):

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
        track = Utils.required(self, 'track')
        toid = Utils.required(self, 'toid')
        friend = False
        if self.request.get('friend'):
            friend = bool(self.request.get('friend'))

        # check password
        if self.error == '' and passwd != config.testing['passwd']:
            self.error = 'passwd is incorrect.'

        start_time = time.time()												# start count

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
            logging.warn('creating new challenge with' + player.uuid )
            challenge = Challenge.Create(self, track, player.uuid, toid, friend)
            if challenge is not None:
                Challenge.ComposeChallenge(self, challenge)

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