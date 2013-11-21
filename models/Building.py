# built-in libraries
import json
import logging

# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache

# config
from config				import config
from Data import Data
from GCVars import GCVars

# enum ItemType
class BUILDING_STATUS(object):
    PENDING = "pending"
    DELIVERED = "delivered"
    OWNED = "owned"
    PRODUCED = "produced"
    PRODUCED_PARTIAL = "produced_partial"

class Building(db.Model):
    uuid = db.StringProperty()
    itid = db.StringProperty()
    inid = db.StringProperty(indexed=False)
    level = db.IntegerProperty(indexed=False)
    status = db.StringProperty()
    amount = db.IntegerProperty(indexed=False)
    location = db.TextProperty(indexed=False)
    timestamp = db.IntegerProperty(indexed=False)
    created = db.DateTimeProperty(auto_now_add=True)

    BuildingStatus = BUILDING_STATUS

    @staticmethod
    def newbuilding(self):
        return Building(parent=db.Key.from_path('Building', config.db['buildingdb_name']))

    @staticmethod
    def getmybuildings(self, uuid):
        buildings = memcache.get(config.db['buildingdb_name']+'.'+uuid)
        if buildings is None:
            buildings = Building.all().filter('uuid =', uuid).ancestor(db.Key.from_path('Building', config.db['buildingdb_name']))
            if not memcache.add(config.db['buildingdb_name']+'.'+uuid, buildings, config.memcache['holdtime']):
                logging.warning('Building - memcache set buildings failed')
        return buildings

    @staticmethod
    def getmybuilding(self, uuid, inid):
        building = memcache.get(config.db['buildingdb_name']+'.'+uuid+'.'+inid)
        if building is None:
            buildings = Building.getmybuildings(self, uuid)
            for item in buildings:
                if item.inid == inid:
                    building = item
                    break
            if building is not None:
                if not memcache.add(config.db['buildingdb_name']+'.'+uuid+'.'+inid, building, config.memcache['holdtime']):
                    logging.warning('Building - memcache set building '+inid+' failed')
        if building is None:
            self.error = 'Building='+inid+' was not found!'
        return building

    @staticmethod
    def setmybuilding(self, building):
        if building.put():
            memcache.delete(config.db['buildingdb_name']+'.'+building.uuid+'.'+building.inid)

    @staticmethod
    def list(self, uuid):
        buildings = memcache.get(config.db['buildingdb_name']+'.'+uuid)
        if buildings is None:
            buildings = Building.all().filter('uuid =', uuid).ancestor(db.Key.from_path('Building', config.db['buildingdb_name']))
            if buildings is not None:
                if not memcache.set(config.db['buildingdb_name']+'.'+uuid, buildings, config.memcache['holdtime']):
                    logging.warning('Building - Set memcache for list buildings failed.')
            else:
                self.error = 'There is no building belongs to uuid="'+uuid+'".'
                return None
        return buildings

    @staticmethod
    def get(self, buid):
        building = memcache.get(config.db['buildingdb_name']+'.'+buid)
        if building is None:
            buildings = Building.all().filter('inid =', buid).ancestor(db.Key.from_path('Building', config.db['buildingdb_name']))
            if buildings is not None:
                bulding = buildings[0]
                #car.data_obj = json.loads(car.data)
                if not memcache.set(config.db['buildingdb_name']+'.'+buid, bulding, config.memcache['holdtime']):
                    logging.warning('Building - Set memcache for get building failed.')
            else:
                self.error = 'Car buid="'+buid+'" does not exist.'
                return None
        return building

    @staticmethod
    def compose_mybuilding(txt, mybuilding):
        if mybuilding.amount is None:
            mybuilding.amount = 0
        txt += '{"inid":"'+mybuilding.inid+'",'
        txt += '"itid":"'+mybuilding.itid+'",'
        txt += '"level":'+str(mybuilding.level)+','
        txt += '"status":"'+mybuilding.status+'",'
        txt += '"location":"'+mybuilding.location+'",'
        txt += '"amount":"'+str(mybuilding.amount)+'",'
        txt += '"timestamp":'+str(mybuilding.timestamp)
        txt += '},'
        return txt

    @staticmethod
    def save_resource_to_building(self, lang, version, uuid, track, score):
        logging.debug('save_resource_to_building uuid:' + uuid + ' track:' + track + ' score:' + str(score) )
         # get all buildings types
        buildings = Data.getbuildings(self, lang, version)

        # get player buildings
        my_buildings = Building.getmybuildings(self, uuid)

        #find the building with the track id and give it cash
        if buildings is not None and my_buildings is not None:
            for my_building in my_buildings:
                # for example:  "itid": "track.1",
                if my_building.itid == track:
                    if my_building.amount is None:
                        my_building.amount = 0
                    logging.debug('save_resource_to_building my_building.amount '+ str(my_building.amount) + '+=' + str(score) )
                    my_building.amount += int(score)
                    my_building.status = Building.BuildingStatus.PRODUCED
                    Building.setmybuilding(self, my_building)

                    return my_building
()