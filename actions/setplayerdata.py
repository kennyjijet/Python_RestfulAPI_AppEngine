# built-in libraries
import webapp2
import logging
import time
import json

# config
from config import config
from GCVars import GCVars

# include
from helpers.utils import Utils
from models.Player import Player
from models.Score import Score
from models.Data import Data
from models.Building import Building

# class implementation
class setplayerdata(webapp2.RequestHandler):
    description = "I am an API to save non gameplay data to a player"
    output = "player state object"
    # standard variables
    game = ''
    sinfo = ''
    respn = ''
    error = ''
    debug = ''

    # get function implementation
    def get(self):
        Utils.reset(self)                                                        # reset/clean standard variables

        # validate and assign parameters
        passwd = Utils.required(self, GCVars.passwd)
        guid = self.request.get('guid')
        uuid = Utils.required(self, 'uuid')
        key = Utils.required(self, 'key')
        val = Utils.required(self, 'val')

        Utils.LogRequest(self)
        # check password
        if self.error == '' and passwd != config.testing['passwd']:
            self.error = 'passwd is incorrect.'

        start_time = time.time()                                                # start count

        # if error, skip this
        if self.error != '' or self.error is None:
            player = Player.getplayer(self, uuid)

            if player is not None and guid != '':
                if guid != player.state_obj['guid']:
                    player = None
                    self.error = config.error_message['dup_login']

        if player is not None:
            data = {}
            if player.state_obj.has_key('data'):
                data = json.loads(player.state_obj['data'])

            data.setdefault(key,val)

            player.state_obj.setdefault('data', json.dumps(data))

            Player.setplayer(self, player)
            self.respn = '{"state":' + player.state + '}'

        else:
            self.error = 'Cant find a player for ' + uuid

        # calculate time taken and return the result
        time_taken = time.time() - start_time
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(Utils.RESTreturn(self, time_taken))

# do exactly as get() does
def post(self):
    self.get()
