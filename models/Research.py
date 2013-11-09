# built-in libraries
import json
import logging

# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache

# config
from config				import config

# enum ItemType
class RESEARCH_STATUS(object):
    PENDING = "pending"
    DELIVERED = "delivered"
    OWNED = "owned"

class Research(db.Model):
    uuid = db.StringProperty()
    itid = db.StringProperty()
    inid = db.StringProperty(indexed=False)
    status = db.StringProperty()
    timestamp = db.IntegerProperty(indexed=False)
    created = db.DateTimeProperty(auto_now_add=True)

    ResearchStatus = RESEARCH_STATUS

    @staticmethod
    def newresearch(self):
        return Research(parent=db.Key.from_path('Research',config.db['researchdb_name']))

    @staticmethod
    def getmyresearches(self, uuid):
        researches = memcache.get(config.db['researchdb_name']+'.'+uuid)
        if researches is None:
            researches = Research.all().filter('uuid =', uuid).ancestor(db.Key.from_path('Research',config.db['researchdb_name']))
            if not memcache.add(config.db['researchdb_name']+'.'+uuid, researches, config.memcache['holdtime']):
                logging.warning('Ressearch - memcache set researches failed')
        return researches

    @staticmethod
    def getmyresearch(self, uuid, inid):
        research = memcache.get(config.db['researchdb_name']+'.'+uuid+'.'+inid)
        if research is None:
            researches = Research.getmyresearches(self, uuid)
            for item in researches:
                if item.inid == inid:
                    research = item
                    break
            if research is not None:
                if not memcache.add(config.db['researchdb_name']+'.'+uuid+'.'+inid, research, config.memcache['holdtime']):
                    logging.warning('Research - memcache set research='+inid+' failed')
        if research is None:
            self.error = 'Research='+inid+' was not found!'
        return research

    @staticmethod
    def setmyresearch(self, research):
        if research.put():
            memcache.delete(config.db['researchdb_name']+'.'+research.uuid+'.'+research.inid)

    @staticmethod
    def compose_myresearch(txt, myresearch):
        txt += '{"inid":"'+myresearch.inid+'",'
        txt += '"itid":"'+myresearch.itid+'",'
        txt += '"status":"'+myresearch.status+'",'
        txt += '"timestamp":'+str(myresearch.timestamp)
        txt += '},'
        return txt
