""" Challenge model class

Project: GrandCentral-GAE
Author: Plus Pingya
Github: https://github.com/Gamepunks/grandcentral-gae

"""

# built-in libraries
import json
import logging
from datetime import datetime

# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache

# config
from config import config

from helpers.utils import Utils

# enum ChallengeType
class CHALLENGE_TYPE(object):
	OPEN_GAME = "open_game"
	PLAYER1_FINISH = "player1_finish"
	PLAYER2_FINISH = "player2_finish"
	BOTH_PLAYERS_FINISH = "both_players_finish"

# class implementation
class Challenge(db.Model):

	id = db.StringProperty()
	track = db.StringProperty()
	uid1 = db.StringProperty()
	uid2 = db.StringProperty()
	state = db.StringProperty()
	data = db.TextProperty(indexed=False)
	created = db.DateTimeProperty(auto_now_add=True)

	ChallengeType = CHALLENGE_TYPE

	@staticmethod
	def Create(self, track, uid1, uid2):
		""" Parameters
			track - id of the race track
			uid1 - user id for player 1, eg fbid
			uid2 - user id for player 2, eg fbid
		"""
		challenge = memcache.get(config.db['challengedb_name']+'.'+track+'.'+uid1+'.'+uid2)
		if challenge is None:
			challenges = Challenge.all().filter('track =', track).filter('uid1 =', uid1).filter('uid2 =', uid2).filter('state !=', CHALLENGE_TYPE.BOTH_PLAYERS_FINISH).ancestor(db.Key.from_path('Challenge', config.db['challengedb_name'])).fetch(1)
			if len(challenges) > 0:
				challenge = challenges[0]
		if challenge is None:
			challenge = Challenge(parent=db.Key.from_path('Challenge', config.db['challengedb_name']))
			challenge.id = Utils.genanyid(self, 'c')
			challenge.track = track
			challenge.uid1 = uid1
			challenge.uid2 = uid2
			challenge.state = CHALLENGE_TYPE.OPEN_GAME
			challenge.data = '{"player1":{"lapTime":-1,"raceData":"","created":""},"player2":{"lapTime":-1,"raceData":"","created":""},"result":{}}'
			if challenge.put():
				if not memcache.add(config.db['challengedb_name']+'.'+track+'.'+uid1+'.'+uid2, challenge, config.memcache['holdtime']):
					logging.warning('Challenge - Set memcache for challenge failed!')
				memcache.delete(config.db['challengedb_name']+'.'+challenge.id)
				if not memcache.add(config.db['challengedb_name']+'.'+challenge.id, challenge, config.memcache['holdtime']):
					logging.warning('Challenge - Set memcache for challenge by Id failed!')
		return challenge

	@staticmethod
	def GetChallenge(self, chid):
		""" Parameters:
			chid - Challenge Id
		"""
		challenge = memcache.get(config.db['challengedb_name']+'.'+chid)
		if challenge is None:
			challenges = Challenge.all().filter('id =', chid).filter('state !=', CHALLENGE_TYPE.BOTH_PLAYERS_FINISH).ancestor(db.Key.from_path('Challenge', config.db['challengedb_name'])).fetch(1)
			if len(challenges) > 0:
				challenge = challenges[0]
				if not memcache.add(config.db['challengedb_name']+'.'+chid, challenge, config.memcache['holdtime']):
					logging.warning('Challenge - Set memcache for challenge by Id failed (Update)!')
		if challenge is None:
			self.error = 'Challenge Id='+chid+' could not be found.'
		return challenge

	@staticmethod
	def GetChallenging(self, uid1):
		""" Parameters
			track - id of the race track
			uid1 - user id of player 1, eg fbid
		"""
		challenging = memcache.get(config.db['challengedb_name']+'.'+uid1+'.challenging')
		if challenging is None:
			challenging = Challenge.all().filter('uid1 =', uid1).filter('state !=', CHALLENGE_TYPE.BOTH_PLAYERS_FINISH).ancestor(db.Key.from_path('Challenge', config.db['challengedb_name']))
			if not memcache.add(config.db['challengedb_name']+'.'+uid1+'.challenging', challenging, config.memcache['holdtime']):
				logging.warning('Challenge - Set memcache for challenging failed!')
		return challenging

	@staticmethod
	def GetChallengers(self, uid2):
		""" Parameters
			track - id of the race track
			uid2 - user id of player 2, eg fbid
		"""
		challengers = memcache.get(config.db['challengedb_name']+'.'+uid2+'.challengers')
		if challengers is None:
			challengers = Challenge.all().filter('uid2 =', uid2).filter('state !=', CHALLENGE_TYPE.BOTH_PLAYERS_FINISH).ancestor(db.Key.from_path('Challenge', config.db['challengedb_name']))
			if not memcache.add(config.db['challengedb_name']+'.'+uid2+'.challengers', challengers, config.memcache['holdtime']):
				logging.warning('Challenge - Set memcache for challengers failed!')
		return challengers

	@staticmethod
	def GetCompleted(self, uid):
		""" Parameter
		 uid - User ID
		"""
		completed = memcache.get(config.db['challengedb_name']+'.'+uid+'.completed')
		if completed is None:
			completed = []
			complete1 = Challenge.all().filter('uid1 =', uid).filter('state =', CHALLENGE_TYPE.BOTH_PLAYERS_FINISH).ancestor(db.Key.from_path('Challenge', config.db['challengedb_name']))
			if complete1 is not None:
				completed += complete1
			complete2 = Challenge.all().filter('uid2 =', uid).filter('state =', CHALLENGE_TYPE.BOTH_PLAYERS_FINISH).ancestor(db.Key.from_path('Challenge', config.db['challengedb_name']))
			if complete2 is not None:
				completed += complete2
			if not memcache.add(config.db['challengedb_name']+'.'+uid+'.completed', completed, config.memcache['holdtime']):
				logging.warning('Challenge - Set memcache for completed failed!')
		return completed

	@staticmethod
	def ComposeChallenge(self, challenge):
		self.respn = '{"info":{'
		self.respn += '"id":"'+challenge.id+'",'
		self.respn += '"track":"'+challenge.track+'",'
		self.respn += '"uid1":"'+challenge.uid1+'",'
		self.respn += '"uid2":"'+challenge.uid2+'",'
		self.respn += '"state":"'+challenge.state+'",'
		self.respn += '"created":"'+str(challenge.created)+'"'
		self.respn += '},"game":'+challenge.data+'}'
		return self.respn

	@staticmethod
	def Update(self, chid, type, uid, laptime, racedata):
		""" Parameters:
			chid - Challenge Id
			type - type of update, 'challenge' or 'accept'
			laptime - laptime that this player made
			racedata - racing data for this player (used in race scene)
		"""
		challenge = memcache.get(config.db['challengedb_name']+'.'+chid)
		if challenge is None:
			challenges = Challenge.all().filter('id =', chid).filter('state !=', CHALLENGE_TYPE.BOTH_PLAYERS_FINISH).ancestor(db.Key.from_path('Challenge', config.db['challengedb_name'])).fetch(1)
			if len(challenges) > 0:
				challenge = challenges[0]
				if not memcache.add(config.db['challengedb_name']+'.'+chid, challenge, config.memcache['holdtime']):
					logging.warning('Challenge - Set memcache for challenge by Id failed (Update)!')
		if challenge is not None:
			game = json.loads(challenge.data)
			_player = 'player1'
			if type != 'challenge':
				_player = 'player2'
			if (_player == 'player1' and challenge.uid1 == uid and (challenge.state == CHALLENGE_TYPE.OPEN_GAME or challenge.state == CHALLENGE_TYPE.PLAYER2_FINISH)) \
				or (_player == 'player2' and challenge.uid2 == uid and (challenge.state == CHALLENGE_TYPE.OPEN_GAME or challenge.state == CHALLENGE_TYPE.PLAYER1_FINISH)):
				game[_player]['lapTime'] = laptime
				game[_player]['raceData'] = racedata
				game[_player]['created'] = str(datetime.now())
			if game['player1']['lapTime'] != -1:
				challenge.state = CHALLENGE_TYPE.PLAYER1_FINISH
			if game['player2']['lapTime'] != -1:
				challenge.state = CHALLENGE_TYPE.PLAYER2_FINISH
			if game['player1']['lapTime'] == -1 and game['player2']["lapTime"] == -1:
				challenge.state = CHALLENGE_TYPE.OPEN_GAME
			if game['player1']['lapTime'] != -1 and game['player2']["lapTime"] != -1:
				challenge.state = CHALLENGE_TYPE.BOTH_PLAYERS_FINISH
			challenge.data = json.dumps(game)
			if challenge.put():
				memcache.delete(config.db['challengedb_name']+'.'+challenge.id)
				if not memcache.add(config.db['challengedb_name']+'.'+challenge.id, challenge):
					logging.warning('Challenge - Set memcache for challenge by Id failed!')
		else:
			self.error = 'Challenge ID='+chid+' could not be found.'
		return challenge

	@staticmethod
	def DeleteById(self, chid):
		""" Parameters:
			chid - Challenge Id
		"""
		challenge = memcache.get(config.db['challengedb_name']+'.'+chid)
		if challenge is None:
			challenges = Challenge.all().filter('id =', chid).filter('state !=', CHALLENGE_TYPE.BOTH_PLAYERS_FINISH).ancestor(db.Key.from_path('Challenge', config.db['challengedb_name'])).fetch(1)
			if len(challenges) > 0:
				challenge = challenges[0]
		if challenge is not None:
			challenge.delete()
			return True
		return False

	@staticmethod
	def DeleteByUserId(self, uid):
		""" Parameters:
			uid - User Id
		"""
		deleted = False
		challenging = Challenge.all().filter('uid1 =', uid).ancestor(db.Key.from_path('Challenge', config.db['challengedb_name']))
		if challenging is not None:
			for challenge in challenging:
				challenge.delete()
				deleted = True
		challengers = Challenge.all().filter('uid2 =', uid).ancestor(db.Key.from_path('Challenge', config.db['challengedb_name']))
		if challengers is not None:
			for challenge in challengers:
				challenge.delete()
				deleted = True
		return deleted