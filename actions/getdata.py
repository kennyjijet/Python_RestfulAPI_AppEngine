""" getdata action class

    Project: GrandCentral-GAE
    Author: Plus Pingya
    Github: https://github.com/Gamepunks/grandcentral-gae


    Description
    ---------------------------------------------------------------
    I am an API to get game data(s) (Data deployed from Google Drive
    Custom Backend


    Input:
    ---------------------------------------------------------------
    required: passwd, type,
    optional: version, lang


    Output:
    ---------------------------------------------------------------
    requested game data(s)


"""

# built-in libraries
import logging
import time
import json

import webapp2


# config
from config import config

# include
from helpers.utils import Utils
from models.Data import Data

# class implementation
class getdata(webapp2.RequestHandler):
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
        type = Utils.required(self, 'type')
        version = config.data_version['building']
        if self.request.get('version'):
            version = self.request.get('version')
        lang = config.server["defaultLanguage"]
        if self.request.get('lang'):
            lang = self.request.get('lang')

        # check password
        if self.error == '' and passwd != config.testing['passwd']:
            self.error = 'passwd is incorrect.'

        start_time = time.time()                                                # start count

        # if error, skip this
        if self.error == '':
            if type == 'all':
                type = ''
                for item in config.gamedata:
                    type += item + ','
                type = type.rstrip(',')

            self.respn = '{'
            types = type.split(',')
            for item in types:
                if (item == 'transui'):
                    data = Data.getData(self, item, version)
                    if data is not None:
                        data_obj = json.loads(data.data)
                        self.respn += '"transui":' + json.dumps(data_obj[lang]) + ','
                else:
                    data = Data.getData(self, item + '_' + lang, version)
                    if data is not None:
                        self.respn += '"' + item + '":' + data.data + ','
                    else:
                        data = Data.getData(self, item, version)
                    if data is not None:
                        self.respn += '"' + item + '":' + data.data + ','
        self.respn = self.respn.rstrip(',') + '}'

        # calculate time taken and return the result
        time_taken = time.time() - start_time
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(Utils.RESTreturn(self, time_taken))

    # do exactly as get() does
    def post(self):
        self.get()