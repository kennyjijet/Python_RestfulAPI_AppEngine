# built-in libraries
import json
import collections
import logging

# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache

# config
from config				import config

class Data(db.Model):

	version = db.FloatProperty()
	type = db.StringProperty()
	data = db.TextProperty()
	created = db.DateTimeProperty(auto_now_add=True)

	@staticmethod
	def newData(self):
		return Data(parent=db.Key.from_path('Data', config.db['datadb_name']))

	@staticmethod
	def getData(self, type, version):
		data = memcache.get(config.db['datadb_name']+'.'+type+'.'+str(version))
		if data is None:
			datas = Data.all().filter('type =', type).filter('version =', version).ancestor(db.Key.from_path('Data', config.db['datadb_name'])).fetch(1)
			if len(datas) >= 1:
				data = datas[0]
				if not memcache.add(config.db['datadb_name']+'.'+type+'.'+str(version), data, config.memcache['longtime']):
					logging.warning('Data - Memcache set data '+type+'.'+str(version)+' failed!')
			else:
				self.error = 'Data '+type+' (v.'+str(version)+') couldn\'t be retrieved!'
				data = None
		return data

	@staticmethod
	def getDataAsObj(self, type, version):
		data = memcache.get(config.db['datadb_name']+'.'+type+'_obj.'+str(version))
		if data is None:
			datas = Data.all().filter('type =', type).filter('version =', version).ancestor(db.Key.from_path('Data', config.db['datadb_name'])).fetch(1)
			if len(datas) >= 1:
				data = datas[0]
				data.obj = json.loads(data.data)
				if not memcache.add(config.db['datadb_name']+'.'+type+'_obj.'+str(version), data, config.memcache['longtime']):
					logging.warning('Data - Memcache set data '+type+'.'+str(version)+' as object failed!')
			else:
				self.error = 'Data '+type+' (v.'+str(version)+') couldn\'t be retrieved!'
				data = None
		return data

	@staticmethod
	def setData(self, idata):
		if idata:
			if idata.put():
				memcache.flush_all()
				"""
				memcache.delete(config.db['datadb_name']+'.'+idata.type+'.'+str(idata.version))
				if not memcache.add(config.db['datadb_name']+'.'+idata.type+'.'+str(idata.version), idata, config.memcache['longtime']):
					logging.warning('Data - Memcache set data '+idata.type+'.'+str(idata.version)+' failed!')
				"""
				return True
		return False

	###############################################################################
	### Buildings
	@staticmethod
	def getbuildings(self, lang, ver):
		buildings = memcache.get('building_'+lang+'.'+str(ver))
		if buildings is None:
			buildings = Data.getData(self, 'building_'+lang, ver)
			if buildings is not None:
				buildings.as_obj = json.loads(buildings.data);
				_buildings = {}
				for list in buildings.as_obj:
					_buildings[list[0]['id']] = []
					for item in list:
						_buildings[list[0]['id']].append(item)
				buildings.as_obj = _buildings
				if not memcache.add('building_'+lang+'.'+str(ver), buildings, config.memcache['longtime']):
					logging.warning('Data.getbuildings memcache set failed!')
			else:
				self.error = 'Building data ('+str(ver)+') couldn\'t be retrieved!'
		return buildings

	###############################################################################
	### Cars
	@staticmethod
	def getcars(self, lang, ver):
		cars = memcache.get('cars_'+lang+'.'+str(ver))
		if cars is None:
			cars = Data.getData(self, 'cars_'+lang, ver)
			if cars is not None:
				cars.as_obj = json.loads(cars.data)
				if not memcache.add('cars_'+lang+'.'+str(ver), cars, config.memcache['longtime']):
					logging.warning('Data.getcars memcache set failed!')
			else:
				self.error = 'Cars data ('+str(ver)+') couldn\'t be retrieved!'
		return cars

	###############################################################################
	### Cars
	@staticmethod
	def getupgrades(self, lang, ver):
		upgrades = memcache.get('upgrades_'+lang+'.'+str(ver))
		if upgrades is None:
			upgrades = Data.getData(self, 'upgrades_'+lang, ver)
			if upgrades is not None:
				upgrades.as_obj = json.loads(upgrades.data)
				if not memcache.add('upgrades_'+lang+'.'+str(ver), upgrades, config.memcache['longtime']):
					logging.warning('Data.getupgrades memcache set failed!')
			else:
				self.error = 'Upgrades data ('+str(ver)+') couldn\'t be retrieved!'
		return upgrades

	"""
	@staticmethod
	def setbuildings(self, ver, buildings):
		buildings.data = json.dumps(buildings.as_obj)
		if buildings.put():
			memcache.delete('buildings.'+str(ver))
			if not memcache.add('buildings_as_obj.'+str(ver), buildings, config.memcache['longtime']):
				logging.warning('Data.setbuildings memcache set failed!')
			return True
		return False
	"""

	###############################################################################
	### Researches
	@staticmethod
	def getresearches(self, lang, ver):
		researches = memcache.get('researches_'+lang+'.'+str(ver))
		if researches is None:
			researches = Data.getData(self, 'research_'+lang, ver)
			if researches is not None:
				researches.as_obj = json.loads(researches.data)
				if not memcache.add('researches_'+lang+'.'+str(ver), researches, config.memcache['longtime']):
					logging.warning('Data.getresearches memcache set failed!')
			else:
				self.error = 'Research data ('+str(ver)+') couldn\'t be retrieved!'
		return researches

	###############################################################################
	### Researches
	@staticmethod
	def gettransui(self, ver):
		transuis = memcache.get('transui.'+str(ver))
		if transuis is None:
			transuis = Data.getData(self, 'transui', ver)
			if transuis is not None:
				transuis.as_obj = json.loads(transuis.data, object_pairs_hook=collections.OrderedDict)
				if not memcache.add('transuis.'+str(ver), transuis, config.memcache['longtime']):
					logging.warning('Data.gettransui memcache set transuis failed!')
			else:
				self.error = 'Trans UI data ('+str(ver)+' couldn\'t be retrieved!'
		return transuis


	###############################################################################
	### Soft Store (Item)
	@staticmethod
	def getstoreitem(self, version=config.softstore['version']):
		return Data.getData(self, 'item', version)

	@staticmethod
	def getstoreitem_as_arr(self, version=config.softstore['version']):
		storeitem_arr = memcache.get(config.db['datadb_name']+'_as_arr.item.'+str(version))
		if storeitem_arr is None:
			storeitem = Data.getData(self, 'item', version)
			if storeitem is not None:
				storeitem_arr = json.loads(storeitem.data)
				if not memcache.add(config.db['datadb_name']+'_as_arr.item.'+str(version), storeitem_arr, config.memcache['longtime']):
					logging.warning('Core - Memcache set item.'+str(version)+' as array failed!')
			else:
				self.error = 'item.'+str(version)+' as array data couldn\'t be retrieved!'
		return storeitem_arr

	@staticmethod
	def getstoreitem_as_obj(self, version=config.softstore['version']):
		storeitem_obj = memcache.get(config.db['datadb_name']+'_as_obj.item.'+str(version))
		if storeitem_obj is None:
			storeitem = Data.getData(self, 'item', version)
			if storeitem is not None:
				_storeitem = json.loads(storeitem.data)
				storeitem_obj = {}
				for item in _storeitem:
					storeitem_obj[item['id']] = item
				if not memcache.add(config.db['datadb_name']+'_as_obj.item.'+str(version), storeitem_obj, config.memcache['longtime']):
					logging.warning('Core - Memcache set item.'+str(version)+' as object failed!')
			else:
				self.error = 'item.'+str(version)+' as object data couldn\'t be retrieved!'
		return storeitem_obj

	###############################################################################
	### Event
	@staticmethod
	def getevents_as_obj(self, version=config.event['version']):
		event_obj = memcache.get(config.db['datadb_name']+'_as_obj.event.'+str(version))
		if event_obj is None:
			event = Data.getData(self, 'event', version)
			if event is not None:
				_event = json.loads(event.data)
				event_obj = {}
				for item in _event:
					event_obj[item['id']] = item
				if not memcache.add(config.db['datadb_name']+'_as_obj.event,'+str(version), event_obj, config.memcache['longtime']):
					logging.warning('Data - Memcache set event.'+str(version)+' as object failed!')
			else:
				self.error = 'item.'+str(version)+' as object data couldn\'t be retrieved!'
		return event_obj