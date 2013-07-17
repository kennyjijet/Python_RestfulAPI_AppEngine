# built-in libraries
import json
import logging

# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache

# config
from config				import config

# enum ItemType
class BUILDING_STATUS(object):
	PENDING = "pending"
	DELIVERED = "delivered"
	OWNED = "owned"

class Building(db.Model):
	uuid = db.StringProperty()
	itid = db.StringProperty()
	inid = db.StringProperty(indexed=False)
	level = db.IntegerProperty(indexed=False)
	status = db.StringProperty()
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
			buildings = Car.all().filter('inid =', buid).ancestor(db.Key.from_path('Building', config.db['buildingdb_name']))
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
		txt += '{"inid":"'+mybuilding.inid+'",'
		txt += '"itid":"'+mybuilding.itid+'",'
		txt += '"level":'+str(mybuilding.level)+','
		txt += '"status":"'+mybuilding.status+'",'
		txt += '"location":"'+mybuilding.location+'",'
		txt += '"timestamp":'+str(mybuilding.timestamp)
		txt += '},'
		return txt
