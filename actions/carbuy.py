""" carbuy action class

    Project: GrandCentral-GAE
    Author: Plus Pingya
    Github: https://github.com/Gamepunks/grandcentral-gae


    Description
    ---------------------------------------------------------------
    I am an API to get buy and obtain car


    Input:
    ---------------------------------------------------------------
    required: passwd, uuid, crid
    optional: lang, version


    Output:
    ---------------------------------------------------------------
    obtained car

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
from models.Data import Data
from models.Player import Player
from models.Car import Car

# class implementation
class carbuy(webapp2.RequestHandler):

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
        version = config.data_version['building']
        if self.request.get('version'):
            version = self.request.get('version')
        lang = config.server["defaultLanguage"]
        if self.request.get('lang'):
            lang = self.request.get('lang')
        uuid = Utils.required(self, 'uuid')
        guid = self.request.get('guid')
        crid = Utils.required(self, 'crid')

        # check password
        if self.error == '' and passwd != config.testing['passwd']:
            self.error = 'passwd is incorrect.'

        start_time = time.time()												# start count

        # logical variables
        player = None
        cars = None
        upgrades = None
        car = None
        #mycars = None

        # if error, skip this
        if self.error == '':
            player = Player.getplayer(self, uuid)

        if self.error == '' and player is not None and guid != '':
            if guid != player.state_obj['guid']:
                player = None
                self.error = config.error_message['dup_login']

        if self.error == '' and player is not None:
            cars = Data.getcars(self, lang, float(version))

        if self.error == '' and cars is not None:
            found = False
            for _car in cars.as_obj:
                if _car['id'] == crid:
                    car = _car
                    found = True
                    break
            if found is False:
                self.error = crid + " was not found!"

        if self.error == '' and car is not None:
            mycars = Car.list(self, uuid)
            for _car in mycars:
                data_obj = json.loads(_car.data)
                try:
                    if data_obj['info']['crid'] == crid:

                        #self.respn = '{"warning":"You have already purchased this car."}'
                        player.state_obj['current_car'] = _car.cuid
                        player.state_obj['updated'] = start_time
                        if Player.setplayer(self, player):
                            self.respn = '{"state":'+player.state+','
                            self.respn += '"car":['
                            self.respn = Car.compose_mycar(self.respn, _car)
                            self.respn = self.respn.rstrip(',') + ']'
                            self.respn += '}'
                            car = None
                        break
                except KeyError:
                    self.error = 'Cannot find crid (KeyError issue), please report admin!'

        if self.error == '' and car is not None:
            upgrades = Data.getupgrades(self, lang, float(version))

        if self.error == '' and upgrades is not None:

            if player.state_obj['cash'] >= car['cost']:
                player.state_obj['cash'] -= car['cost']
                player.state_obj['updated'] = start_time 						# update timestamp for player

                mycar = Car.create(self, player.uuid)
                mycar.data_obj['info'] = {'crid': car['id']}
                mycar.data_obj['upgrades'] = []
                mycar.data_obj['equip'] = {}
                player.state_obj['current_car'] = mycar.cuid
                default_upgrades = car['default_upgrades'].replace(' ', '').split(',')

                for default_upgrade in default_upgrades:
                    mycar.data_obj['upgrades'].append(default_upgrade)
                    for _type in upgrades.as_obj:
                        try:
                            mycar.data_obj['equip'][type]
                        except KeyError:
                            for upgrade in upgrades.as_obj[_type]:
                                if upgrade['id'] == default_upgrade:
                                    mycar.data_obj['equip'][_type] = default_upgrade
                                    break
                                    break

                if Player.setplayer(self, player):
                    if Car.update(self, mycar):
                        self.respn = '{"state":'+player.state+','
                        self.respn += '"car":['
                        self.respn = Car.compose_mycar(self.respn, mycar)
                        self.respn = self.respn.rstrip(',') + ']'
                        self.respn += '}'

            else:
                self.respn = '{"warning":"not enough cash!"}'

        # calculate time taken and return the result
        time_taken = time.time() - start_time
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(Utils.RESTreturn(self, time_taken))

    # do exactly as get() does
    def post(self):
        self.get()