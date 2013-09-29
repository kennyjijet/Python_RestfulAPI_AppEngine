""" challengedelete action class

    Project: GrandCentral-GAE
    Author: Plus Pingya
    Github: https://github.com/Gamepunks/grandcentral-gae


    Description
    ---------------------------------------------------------------
    I am an API to delete a challenge or delete all give user's challenges


    Input:
    ---------------------------------------------------------------
    required: passwd, uuid,
    optional: chid


    Output:
    ---------------------------------------------------------------
    result = success/failed

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
from models.Player import Player
from models.Challenge import Challenge

# class implementation
class challengedelete(webapp2.RequestHandler):

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
        chid = self.request.get('chid')

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

        result = None
        if self.error == '' and player is not None:
            if chid:
                if Challenge.DeleteById(self, chid):
                    result = '{"result":"delete successfully"}'
                else:
                    result = '{"result":"Challenge Id='+chid+' could not be found, nothing was deleted"}'
            else:
                if Challenge.DeleteByUserId(self, player.uuid):
                    result = '{"result":"delete successfully"}'
                elif Challenge.DeleteByUserId(self, player.fbid):
                    result = '{"result":"delete successfully"}'
                else:
                    result = '{"result":"nothing was deleted"}'

        if self.error == '' and player is not None:
            Challenge.ComposeChallenges(self, player)
            self.respn += result
            self.respn = self.respn.rstrip(',') + ']}'

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