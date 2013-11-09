
# built-in libraries
import time

import webapp2


# built-in libraries

# google's libraries
from google.appengine.ext import db

from google.appengine.api import namespace_manager

# config
from config import config

# include
from helpers.utils import Utils
from models.Data import Data

# class implementation
class deploy_pro7(webapp2.RequestHandler):
    # standard variables
    sinfo = ''
    respn = ''
    error = ''
    debug = ''

    # get function implementation
    def get(self):
        Utils.reset(self)                                                               # reset/clean standard variables
        self.game = 'pro7'
        namespace_manager.set_namespace(self.game)

        # validate and assign parameters
        passwd = Utils.required(self, 'passwd')
        type = Utils.required(self, 'type')
        version = Utils.required(self, 'version')
        data = Utils.required(self, 'data')

        # required password to process this action
        if self.error == '' and passwd != config.testing['passwd']:
            self.error = 'passwd is incorrect.'

        start_time = time.time()                                                         # start count

        # set default parameter
        idata = None

        # if any error, skip this
        if self.error == '':
            idata = Data.getData(self, type, float(version))                             # get data from memcache or datastore

        if idata is None:                                                              	 # if no data was found
            idata = Data.newData(self)      											 # create a new one
            idata.type = type                                                            # assign type
            idata.version = float(version)                                               # assign version
            self.error = ''                                                              # clean error

        # if any error or idata is none, then skip to the end
        if self.error == '' and idata is not None:
            idata.data = data                                                            # assign lastest deployed data
            if Data.setData(self, idata):                                                # put or update in database and memcache
                self.respn = '"Deploy successfully!"'                                    # tell user that his request is success
            else:                                                                        # or
                self.error = 'Deploy failed - couldn\'t update database!'                # tell him that his required is failed

        # calculate time taken and return the result
        time_taken = time.time() - start_time
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(Utils.RESTreturn(self, time_taken))

    # do exactly as get() does
    def post(self):
        self.get()