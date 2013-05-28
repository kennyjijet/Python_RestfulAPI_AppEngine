# built-in libraries
import json
import logging

# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache

# config
from config				import config

# enum ItemType
class ITEMTYPE(object):
    BUILDING        = "Building"

class Item(db.Model):
    uuid 			= db.StringProperty()
    itid			= db.StringProperty()
    inid 			= db.StringProperty(indexed=False)
    status			= db.StringProperty()
    userData        = db.TextProperty(indexed=False)
    timestamp		= db.FloatProperty(indexed=False)
    created			= db.DateTimeProperty(auto_now_add=True)

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