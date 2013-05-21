# built-in libraries
import json
import logging

# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache

# config
from config				import config

class Data(db.Model):
    version             = db.FloatProperty()
    type				= db.StringProperty()
    data 				= db.TextProperty()
    created				= db.DateTimeProperty(auto_now_add=True)

    @staticmethod
    def getData(self, type, version):
        data = memcache.get(config.db['datadb_name']+'.'+type+'.'+str(version))
        if data is None:
            datas = Data.all().filter('type =', type).filter('version =', version).ancestor(db.Key.from_path('Data', config.db['datadb_name'])).fetch(1)
            if len(datas) >= 1:
                logging.info('3')
                data = datas[0]
                if not memcache.add(config.db['datadb_name']+'.'+type+'.'+str(version), data, config.memcache['longtime']):
                    logging.warning('Data - Memcache set data '+type+'.'+str(version)+' failed!')
            else:
                self.error = 'Data '+type+' (v.'+str(version)+') couldn\'t be retrieved!'
                data = None
        return data

    @staticmethod
    def setData(self, idata):
        if idata:
            if idata.put():
                memcache.delete(config.db['datadb_name']+'.'+idata.type+'.'+str(idata.version))
                if not memcache.add(config.db['datadb_name']+'.'+idata.type+'.'+str(idata.version), idata, config.memcache['longtime']):
                    logging.warning('Data - Memcache set data '+idata.type+'.'+str(idata.version)+' failed!')
                return True
        return False

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