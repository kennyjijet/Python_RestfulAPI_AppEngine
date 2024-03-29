""" Player model class

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

# class implementation
class Player(db.Model):

    uuid = db.StringProperty()
    fbid = db.StringProperty()
    info = db.StringProperty(indexed=False)
    state = db.TextProperty(indexed=False)
    updated = db.DateTimeProperty(auto_now_add=True)
    game = db.StringProperty()

    @staticmethod
    def getplayer(self, uuid):
        #player = memcache.get(config.db['playerdb_name']+'.'+uuid)
        # removed player memcache due to lost car bug
        player = None
        if player is None:
            players = Player.all().filter('uuid =', uuid).ancestor(db.Key.from_path('Player',config.db['playerdb_name'])).fetch(1)
            if len(players) >= 1:
                player = players[0]
                player.info_obj = json.loads(player.info)
                player.state_obj = json.loads(player.state)
                if not memcache.add(config.db['playerdb_name']+'.'+uuid, player, config.memcache['holdtime']):
                    logging.warning('Player - Memcache set player failed')

            else:
                self.error = 'uuid='+uuid+' was not found.'
                player = None

        if player:
            logging.debug('getting player ' + player.state)
        else:
            logging.debug('no player')
        return player

    @staticmethod
    def getplayerByFbid(self, fbid):
        if fbid != '':
            #player = memcache.get(config.db['playerdb_name']+'.'+fbid)
            # removed player memcache due to lost car bug
            player = None
            if player is None:
                players = Player.all().filter('fbid =', fbid).ancestor(db.Key.from_path('Player', config.db['playerdb_name'])).fetch(1);
                if len(players) >= 1:
                    player = players[0]
                    player.info_obj = json.loads(player.info)
                    player.state_obj = json.loads(player.state)
                    if not memcache.add(config.db['playerdb_name']+'.'+fbid, player, config.memcache['holdtime']):
                        logging.warning('Player - Memcache set player failed')
                else:
                    #self.error = 'fbid='+fbid+' was not found.'
                    player = None
            return player
        return None

    @staticmethod
    def setplayer(self, player):
        player.info = json.dumps(player.info_obj)
        player.state = json.dumps(player.state_obj)
        logging.debug('setting player ' + player.state)
        if player.put():
            memcache.delete(config.db['playerdb_name']+'.'+player.uuid)
            if not memcache.add(config.db['playerdb_name']+'.'+player.uuid, player, config.memcache['holdtime']):
                logging.warning('Player - Memcache set player failed')
            return True
        else:
            logging.error('Player - not saved')
        return False

    @staticmethod
    def compose_player(self, player):
        self.respn = '{'
        self.respn += '"uuid":"'+player.uuid+'",'
        self.respn += '"fbid":"'+player.fbid+'",'
        self.respn += '"info":'+player.info+','
        self.respn += '"state":'+player.state
        self.respn += '}'

    @staticmethod
    def compose_player_info(self, player):
        self.respn = '{'
        self.respn += '"uuid":"'+player.uuid+'",'
        self.respn += '"fbid":"'+player.fbid+'",'
        self.respn += '"info":'+player.info
        self.respn += '}'

    @staticmethod
    def compose_player_state(self, player):
        self.respn = '{'
        self.respn += '"uuid":"'+player.uuid+'",'
        self.respn += '"fbid":"'+player.fbid+'",'
        self.respn += '"state":'+player.state
        self.respn += '}'