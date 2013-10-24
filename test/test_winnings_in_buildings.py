# built-in libraries
import time

import webapp2

from config import config

# include

from helpers.utils import Utils
from models.Data import Data
from models.Building import Building
from models.Player import Player

# class implementation
class test_winnings_in_buildings(webapp2.RequestHandler):
    # standard variables
    sinfo = ''
    respn = ''
    error = ''
    debug = ''

    # get function implementation

    def get(self):
        Utils.reset(self)
        uuid = Utils.required(self, 'uuid')
        version = config.data_version['building']
        if self.request.get('version'):
            version = self.request.get('version')
        lang = config.server["defaultLanguage"]
        if self.request.get('lang'):
            lang = self.request.get('lang')
        track = 'track.1'
        if self.request.get('track'):
            lang = self.request.get('track')
        score = 0
        if self.request.get('score'):
            lang = self.request.get('score')

        uuid = self.request.get('uuid')

        start_time = time.time()
        # find the right track in buildings and add the score total to it for collection

        player = Player.getplayer(self, uuid)

        # get all buildings types
        buildings = Data.getbuildings(self, lang, version)

        # get player buildings
        mybuildings = Building.getmybuildings(self, uuid)

        #find the building with the track id and give it cash
        if buildings is not None and mybuildings is not None:
            self.respn += '"building":['
            for mybuilding in mybuildings:
                _upd = False
                # for example:  "itid": "track.1",
                if mybuilding.itid == track:
                    mybuilding.amount += score
                    Building.setmybuilding(self, mybuilding)
                self.respn = Building.compose_mybuilding(self.respn, mybuilding)
            self.respn = self.respn.rstrip(',') + '],'

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