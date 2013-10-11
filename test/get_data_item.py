
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
class get_data_item(webapp2.RequestHandler):
    # standard variables
    sinfo = ''
    respn = ''
    error = ''
    debug = ''

    # get function implementation

    def get(self):
        Utils.reset(self)

        lang="en"
        item= Utils.required(self, 'item')
        data = Data.getDataAsObj(self, item, config.data_version['racewinnings'])

        if data is not None:
            self.respn += '"' + item + '":' + data.data + ','
        else:
            data = Data.getData(self, item, vers1ion)
        if data is not None:
            self.respn += '"' + item + '":' + data.data + ','

        self.respn = self.respn.rstrip(',') + '}'
        # calculate time taken and return the result
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(Utils.RESTreturn(self, 1))

    # do exactly as get() does
    def post(self):
        self.get()