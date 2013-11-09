""" Car model class

Project: GrandCentral-GAE
Author: Plus Pingya
Github: https://github.com/Gamepunks/grandcentral-gae

"""

# built-in libraries
import json
import logging

# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache

# config
from config import config

# include
from helpers.utils import Utils

# class implementation
class Car(db.Model):

    cuid = db.StringProperty()
    uuid = db.StringProperty()
    data = db.TextProperty(indexed=False)
    updated = db.DateTimeProperty(auto_now_add=True)

    @staticmethod
    def create(self, uuid):
        car = Car(parent=db.Key.from_path('Car', config.db['cardb_name']))
        car.cuid = Utils.genanyid(self, 'cu')
        car.uuid = uuid
        car.data_obj = {}
        return car

    @staticmethod
    def list(self, uuid):
        cars = memcache.get(config.db['cardb_name']+'.'+uuid)
        if cars is None:
            cars = Car.all().filter('uuid =', uuid).ancestor(db.Key.from_path('Car', config.db['cardb_name']))
            if cars is not None:
                if not memcache.set(config.db['cardb_name']+'.'+uuid, cars, config.memcache['holdtime']):
                    logging.warning('Car - Set memcache for list cars failed.')
            else:
                self.error = 'There is no car belongs to uuid="'+uuid+'".'
                return None
        return cars

    @staticmethod
    def get(self, cuid):
        car = memcache.get(config.db['cardb_name']+'.'+cuid)
        if car is None:
            cars = Car.all().filter('cuid =', cuid).ancestor(db.Key.from_path('Car',config.db['cardb_name']))
            if cars is not None:
                car = cars[0]
                car.data_obj = json.loads(car.data)
                if not memcache.set(config.db['cardb_name']+'.'+car.cuid, car, config.memcache['holdtime']):
                    logging.warning('Car - Set memcache for create car failed.')
            else:
                self.error = 'Car cuid="'+cuid+'" does not exist.'
                return None
        return car

    @staticmethod
    def update(self, car):
        car.data = json.dumps(car.data_obj)
        if car.put():
            memcache.delete(config.db['cardb_name']+'.'+car.cuid)
            if not memcache.set(config.db['cardb_name']+'.'+car.cuid, car, config.memcache['holdtime']):
                logging.warning('Car - Set memcache for update car failed.')
            return True
        return False

    @staticmethod
    def compose_mycar(text, car):
        text += '{'
        text += '"cuid":"'+car.cuid+'",'
        text += '"data":'+car.data
        text += '}'
        return text