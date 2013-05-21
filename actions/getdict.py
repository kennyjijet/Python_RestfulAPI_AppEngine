""" getdict action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae


	Description
	---------------------------------------------------------------
	I am an API to get given language data for game (Data deployed from Google Drive
	Custom Backend


	Input:
	---------------------------------------------------------------
	required: passwd, lang,
	optional: version


	Output:
	---------------------------------------------------------------
	requested language data


"""

# built-in libraries
import webapp2
import logging
import time
import json

# google's libraries
from google.appengine.api import memcache

# config
from config         import config

# include
from helpers.utils  import Utils
from models.Data    import Data

# class implementation
class getdict(webapp2.RequestHandler):

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
        lang = Utils.required(self, 'lang')
        version = self.request.get('version')
        if version is None or version == '':
            version = config.dictionary['version']

        # check password
        if self.error == '' and passwd != config.testing['passwd']:
            self.error = 'passwd is incorrect.'

        start_time = time.time()												# start count

        # if error, skip this
        if self.error == '':
            dict = memcache.get('dictionary.'+lang)
            if dict is None:
                data = Data.getData(self, 'dictionary', float(version))
                if data is not None:
                    obj = json.loads(data.data)
                    dict = {}
                    for i in obj:
                        try:
                            dict[i] = obj[i][lang]
                        except KeyError:
                            self.error = 'Dictionary for give language was not found!'
                            dict = {}
                    if not memcache.add('dictionary.'+lang, dict, config.memcache['longtime']):
                        logging.warning('getdict - Set memcache dictionary.'+lang+' failed!')
            self.respn = json.dumps(dict)

        # calculate time taken and return the result
        time_taken =  time.time() - start_time
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(Utils.RESTreturn(self, time_taken))

    # do exactly as get() does
    def post(self):
        self.get()