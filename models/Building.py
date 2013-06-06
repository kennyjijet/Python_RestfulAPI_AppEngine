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
	REWARD = "reward"
	REWARDED = "rewarded"
	PRODUCED = "produced"
	PRODUCED_PARTIAL = "produced_partial"

class Building(db.Model):
	uuid = db.StringProperty()
	itid = db.StringProperty()
	inid = db.StringProperty(indexed=False)
	status = db.StringProperty()
	location = db.TextProperty(indexed=False)
	timestamp = db.IntegerProperty(indexed=False)
	created = db.DateTimeProperty(auto_now_add=True)

	BuildingStatus = BUILDING_STATUS

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
	def compose_mybuilding(txt, mybuilding):
		txt += '{"inid":"'+mybuilding.inid+'",'
		txt += '"itid":"'+mybuilding.itid+'",'
		txt += '"status":"'+mybuilding.status+'",'
		txt += '"location":"'+mybuilding.location+'",'
		txt += '"timestamp":'+str(mybuilding.timestamp)
		txt += '},'
		return txt;

	"""
    ItemType        = ITEMTYPE

    @staticmethod
    def getitems(self, uuid):
        items = memcache.get(config.db['itemdb_name']+'.'+uuid)
        if items is None:
            items = Item.all().filter('uuid =', uuid).ancestor(db.Key.from_path('Item', config.db['itemdb_name']))
            if not memcache.add(config.db['itemdb_name']+'.'+uuid, items, config.memcache['holdtime']):
                logging.warning('Core - Memcache set items failed')
        return items

    @staticmethod
    def getitembyinid(self, uuid, inid):
        item = memcache.get(config.db['itemdb_name']+'.'+uuid+'.'+inid)
        if item is None:
            items = Item.getitems(self, uuid)
            if items is not None:
                for i in items:
                    if i.inid == inid:
                        item = i
                        if not memcache.add(config.db['itemdb_name']+'.'+uuid+'.'+inid, item, config.memcache['holdtime']):
                            logging.warning('Item - Memcache set item('+inid+') failed')
        return item

    @staticmethod
    def setitem(self, item):
        if item is not None:
            if item.put():
                memcache.delete(config.db['itemdb_name']+'.'+item.uuid+'.'+item.inid)
                if not memcache.add(config.db['itemdb_name']+'.'+item.uuid+'.'+item.inid, item, config.memcache['holdtime']):
                    logging.warning('Item - Memcache set item('+item.inid+') failed')
                return True
        return False

    @staticmethod
    def getspecificitems(self, uuid, itid):
        items = memcache.get(config.db['itemdb_name']+'.'+itid+'.'+uuid)
        if items is None:
            items = Item.all().filter('uuid =', uuid).filter('itid =', itid).ancestor(db.Key.from_path('Item', config.db['itemdb_name']));
            if not memcache.add(config.db['itemdb_name']+'.'+itid+'.'+uuid, items, config.memcache['holdtime']):
                logging.warning('Core - Memcache set specific item failed')
        return items

    @staticmethod
    def getproduceditems(self, uuid):
        items = memcache.get(config.db['itemdb_name']+'_produced.'+uuid)
        if items is None:
            items = Item.all().filter('uuid =', uuid).filter('status =', 'produced').ancestor(db.Key.from_path('Item', config.db['itemdb_name']));
            if not memcache.add(config.db['itemdb_name']+'_produced.'+uuid, items, config.memcache['holdtime']):
                logging.warning('Core - Memcache set produced items failed')
        return items

    @staticmethod
    def getspecificinidproduceditem(self, uuid, inid):
        items = Item.getproduceditems(self, uuid)
        item = None
        for _item in items:
            if _item.inid == inid:
                item = _item
                break


        #if item is not None:

        return item
    """