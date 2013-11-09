""" deleteplayer action class

    Project: GrandCentral-GAE
    Author: Plus Pingya
    Github: https://github.com/Gamepunks/grandcentral-gae


    Description
    ---------------------------------------------------------------
    I am an API to delete player account, this includes
    player state, scores, items, record


    Input:
    ---------------------------------------------------------------
    required: passwd, uuid
    optional:


    Output:
    ---------------------------------------------------------------
    result success or failed

"""

# build-in libraries
import time

import webapp2


# google's libraries
from google.appengine.ext import db

# config
from config import config
import logging

# include
from models.Player import Player
from models.Score import Score
from models.Item import Item
from models.Record import Record
from models.Building import Building
from models.Car import Car
from models.Challenge import Challenge
from helpers.utils import Utils

# class implementation
class clean(webapp2.RequestHandler):

    # standard variables
    game = ''
    sinfo = ''
    respn = ''
    error = ''
    debug = ''

    # get function implementation
    def get(self):
        logging.debug("clean removed")
        """
        start_time = time.time()
        db.delete ( Score.all() )
        db.delete ( Item.all() )
        db.delete ( Record.all() )
        db.delete ( Building.all() )
        db.delete ( Car.all() )
        db.delete ( Challenge.all() )
        db.delete ( Player.all() )
        db.delete ( Record.all() )
        logging.debug("clean complete")
        """

        # calculate time taken and return the result
        time_taken = time.time() - start_time
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(Utils.RESTreturn(self, time_taken))

    # do exactly as get() does
    def post(self):
        self.get()