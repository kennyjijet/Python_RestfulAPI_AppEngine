""" Player model class

Project: GrandCentral-GAE
Author: Plus Pingya
Github: https://github.com/Gamepunks/grandcentral-gae

"""

# built-in libraries
import json

# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache

# config
from config import config

# class implementation
class Player(db.Model):

	uuid = db.StringProperty()
	info = db.StringProperty(indexed=False)
	state = db.TextProperty(indexed=False)
	updated = db.DateTimeProperty(auto_now_add=True)

	"""
	@staticmethod
	def getplayer(self, uuid): 
		player = memcache.get(config.db['playerdb_name']+'.'+uuid)
		if player is None:
			players = Player.all().filter('uuid =', uuid).ancestor(db.Key.from_path('Player', config.db['playerdb_name'])).fetch(1);
			if len(players)>=1:
				player = players[0]
				if not memcache.add(config.db['playerdb_name']+'.'+uuid, player, config.memcache['holdtime']):
					logging.warning('Player - Memcache set player failed')
			else:
				self.error = 'uuid='+uuid+' was not found.'
				player = None
		return player
	"""

	@staticmethod
	def getplayer(self, uuid):
		player = memcache.get(config.db['playerdb_name']+'.'+uuid)
		if player is None:
			players = Player.all().filter('uuid =', uuid).ancestor(db.Key.from_path('Player', config.db['playerdb_name'])).fetch(1);
			if len(players) >= 1:
				player = players[0]
				player.info_obj = json.loads(player.info)
				player.state_obj = json.loads(player.state)
				if not memcache.add(config.db['playerdb_name']+'.'+uuid, player, config.memcache['holdtime']):
					logging.warning('Player - Memcache set player failed')
			else:
				self.error = 'uuid='+uuid+' was not found.'
				player = None
		return player

	@staticmethod
	def setplayer(self, player):
		player.info = json.dumps(player.info_obj)
		player.state = json.dumps(player.state_obj)
		if player.put():
			memcache.delete(config.db['playerdb_name']+'.'+player.uuid)
			if not memcache.add(config.db['playerdb_name']+'.'+player.uuid, player, config.memcache['holdtime']):
				logging.warning('Player - Memcache set player failed')
			return True
		return False

	@staticmethod
	def compose_player(self, player):
		self.respn = '{'
		self.respn += '"uuid":"'+player.uuid+'",'
		self.respn += '"info":'+player.info+','
		self.respn += '"state":'+player.state
		self.respn += '}'

	@staticmethod
	def compose_player_info(self, player):
		self.respn = '{'
		self.respn += '"uuid":"'+player.uuid+'",'
		self.respn += '"info":'+player.info
		self.respn += '}'

	@staticmethod
	def compose_player_state(self, player):
		self.respn = '{'
		self.respn += '"uuid":"'+player.uuid+'",'
		self.respn += '"state":'+player.state
		self.respn += '}'

	@staticmethod
	def compose_player_partial(self, player, partials):
		player_obj = json.loads(player.state)
		partials = partials.replace(' ', '')
		_partials = partials.split(',')
		self.respn = '{'
		self.error = ''
		for k in _partials:
			try:
				self.respn += '"'+k+'":'
				v = player_obj[k]
				if isinstance(v,str) or isinstance(v,unicode):
					self.respn += '"'+player_obj[k]+'",'
				else:
					self.respn += str(player_obj[k])+','
			except KeyError:
				self.respn = ''
				self.error += 'Key: '+k+' does not exist! '
		if self.error == '':
			self.respn = self.respn.rstrip(',') + '}'