""" Challenge model class

Project: GrandCentral-GAE
Author: Plus Pingya
Github: https://github.com/Gamepunks/grandcentral-gae

"""

# built-in libraries
import time
from datetime import datetime
from datetime import timedelta

import json
import logging


# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache

# config
from config import config

# include
from helpers.utils import Utils
from models.Data import Data
from models.Player import Player

# enum ChallengeType
class CHALLENGE_TYPE(object):
    OPEN_GAME = "open_game"
    PLAYER1_FINISH = "player1_finish"
    PLAYER2_FINISH = "player2_finish"
    BOTH_PLAYERS_FINISH = "both_players_finish"
    GAME_OVER = "game_over"

class CHALLENGE_MODE(object):
    CHALLENGE = 'challenge'
    ACCEPT = 'accept'

# class implementation
class Challenge(db.Model):
    id = db.StringProperty()
    track = db.StringProperty()
    uid1 = db.StringProperty()
    uid2 = db.StringProperty()
    state = db.StringProperty()
    data = db.TextProperty(indexed=False)
    created = db.DateTimeProperty(auto_now_add=True, indexed=True)

    ChallengeType = CHALLENGE_TYPE
    ChallengeMode = CHALLENGE_MODE

    @staticmethod
    def Create(self, track, uid1, uid2, name, name2, image, image2, are_they_friend):
        """ Parameters
            track - id of the race track
            uid1 - user id for player 1, could be fbid or uuid
            uid2 - user id for player 2, could be fbid or uuid
        """
        challenge = None
        challenges = Challenge.all().filter('track =', track) \
            .filter('uid1 =', uid1) \
            .filter('uid2 =', uid2). \
            filter('state !=', CHALLENGE_TYPE.GAME_OVER) \
            .ancestor(db.Key.from_path('Challenge', config.db['challengedb_name'])) \
            .fetch(1)

        if len(challenges) > 0:
            challenge = challenges[0]

        if challenge is None:
            challenge = Challenge(parent=db.Key.from_path('Challenge', config.db['challengedb_name']))
            challenge.id = Utils.genanyid(self, 'c')
            challenge.track = track
            challenge.uid1 = uid1
            challenge.uid2 = uid2
            challenge.state = CHALLENGE_TYPE.OPEN_GAME
            challenge.data = '{'
            challenge.data += '"player1":{"player": {"id":"' + uid1 + '"},"name":"' + name + '", "image":"' + image+'"},'
            challenge.data += '"player2":{"player": {"id":"' + uid2 + '"},"name":"' + name2 + '", "image":"' + image2+'"},'
            challenge.data += '"friend":' + str(are_they_friend).lower() + ','
            challenge.data += '"result":{"winner":"pending","player1_seen":false,"player2_seen":false}'
            challenge.data +='}'
            if challenge.put():
                if not memcache.add(config.db['challengedb_name'] + '.' + challenge.id, challenge,
                                    config.memcache['holdtime']):
                    logging.warning('Challenge - Set memcache for challenge by Id failed!')

        return challenge

    @staticmethod
    def GetChallenge(self, chid):
        """ Parameters:
            chid - Challenge Id
        """
        logging.debug("GetChallenge:" + chid)
        challenge = memcache.get(config.db['challengedb_name'] + '.' + chid)
        if challenge is None:
            challenges = Challenge.all().filter('id =', chid).filter('state !=',
                                                                     CHALLENGE_TYPE.BOTH_PLAYERS_FINISH).ancestor(
                db.Key.from_path('Challenge', config.db['challengedb_name'])).fetch(1)
            if len(challenges) > 0:
                challenge = challenges[0]
                if not memcache.add(config.db['challengedb_name'] + '.' + chid, challenge, config.memcache['holdtime']):
                    logging.warning('Challenge - Set memcache for challenge by Id failed (Update)!')
        if challenge is None:
            self.error = 'Challenge Id=' + chid + ' could not be found OR complete.'
        return challenge

    @staticmethod
    def GetChallenging(self, uid1):
        """ Parameters
            track - id of the race track
            uid1 - user id of player 1, eg fbid
        """
        logging.debug("GetChallenging:" + uid1)
        challenging = memcache.get(config.db['challengedb_name'] + '.' + uid1 + '.challenging')
        if challenging is None:
            challenging = Challenge.all().filter('uid1 =', uid1).filter('state !=',
                                                                        CHALLENGE_TYPE.BOTH_PLAYERS_FINISH).ancestor(
                db.Key.from_path('Challenge', config.db['challengedb_name']))

            if not memcache.add(config.db['challengedb_name'] + '.' + uid1 + '.challenging', challenging,
                                config.memcache['holdtime']):
                logging.warning('Challenge - Set memcache for challenging failed!')
        return challenging

    @staticmethod
    def GetChallengers(self, uid2):
        """ Parameters
            track - id of the race track
            uid2 - user id of player 2, eg fbid
        """
        logging.debug("GetChallengers:" + uid2)
        challengers = memcache.get(config.db['challengedb_name'] + '.' + uid2 + '.challengers')
        if challengers is None:
            logging.debug('GetChallengers non memcache')
            challengers = Challenge.all().filter('uid2 =', uid2).filter('state !=',
                                                                        CHALLENGE_TYPE.BOTH_PLAYERS_FINISH).ancestor(
                db.Key.from_path('Challenge', config.db['challengedb_name']))

            if not memcache.add(config.db['challengedb_name'] + '.' + uid2 + '.challengers', challengers,
                                config.memcache['holdtime']):
                logging.warning('Challenge - Set memcache for challengers failed!')
        return challengers

    @staticmethod
    def GetCompleted(self, uid):
        """ Parameter
         uid - User ID
        """
        logging.debug("GetCompleted:" + uid)
        completed = memcache.get(config.db['challengedb_name'] + '.' + uid + '.completed')
        if completed is None:
            completed = []
            complete1 = Challenge.all().filter('uid1 =', uid).filter('state =',
                                                                     CHALLENGE_TYPE.BOTH_PLAYERS_FINISH).ancestor(
                db.Key.from_path('Challenge', config.db['challengedb_name']))
            if complete1 is not None:
                completed += complete1
            complete2 = Challenge.all().filter('uid2 =', uid).filter('state =',
                                                                     CHALLENGE_TYPE.BOTH_PLAYERS_FINISH).ancestor(
                db.Key.from_path('Challenge', config.db['challengedb_name']))
            if complete2 is not None:
                completed += complete2
            if not memcache.add(config.db['challengedb_name'] + '.' + uid + '.completed', completed,
                                config.memcache['holdtime']):
                logging.warning('Challenge - Set memcache for completed failed!')
        return completed



    @staticmethod
    def Update(self, chid, type, uid, laptime, replay, events, cardata, name, image):
        """ Parameters:
            chid - Challenge Id
            type - type of update, 'CHALLENGE' or 'ACCEPT'
            uid - user id, could be fbid or uuid
            replay - racing data
            score - button replay
        """

        logging.debug("Challenge Update with replay length " + str(len(replay)))
        challenge = memcache.get(config.db['challengedb_name'] + '.' + chid)
        if challenge is None:
            logging.debug("Challenge not found in memcache")
            challenges = Challenge.all().filter('id =', chid).filter('state !=', CHALLENGE_TYPE.GAME_OVER).ancestor(
                db.Key.from_path('Challenge', config.db['challengedb_name'])).fetch(1)
            if len(challenges) > 0:
                challenge = challenges[0]
                logging.debug("Challenge found in data")
                if not memcache.add(config.db['challengedb_name'] + '.' + chid, challenge, config.memcache['holdtime']):
                    logging.warning('Challenge - Set memcache for challenge by Id failed (Update)!')

        if challenge is not None:
            logging.debug("Challenge is not none")
            #logging.debug("challenge update :" + challenge.data)
            game = json.loads(challenge.data)
            _upd = False
            if challenge.state != CHALLENGE_TYPE.GAME_OVER:
                logging.info("challenge not over. state = " + challenge.state + " type = " + type)

                start_time = time.time()
                # flag to prevent Player saving outside this function and loosing the changes
                challenge.manual_update = False

                CHALLENGE_TYPE
                _player = 'player1'
                if type != CHALLENGE_MODE.CHALLENGE:
                    _player = 'player2'

                logging.info("updating _player " + _player)

                # find state of challenge
                if (_player == 'player1' and challenge.uid1 == uid and ( challenge.state == CHALLENGE_TYPE.OPEN_GAME or challenge.state == CHALLENGE_TYPE.PLAYER1_FINISH) ) or (_player == 'player2' and challenge.uid2 == uid and ( challenge.state == CHALLENGE_TYPE.OPEN_GAME or challenge.state == CHALLENGE_TYPE.PLAYER2_FINISH)):
                    logging.debug("found the key in the challenge data for the correct player and update the new state")
                    # find the key in the challenge data for the correct player and update the new state
                    game[_player] = {'player': {'id': uid}, 'laptime': float(laptime),
                                     'replay': replay, 'events': events,
                                     'created': start_time, 'cardata': cardata, 'name': name, 'image': image}

                # update challenge state by looking at participants
                if 'replay' in game['player1']:
                    challenge.state = CHALLENGE_TYPE.PLAYER1_FINISH
                if 'replay' in game['player2']:
                    challenge.state = CHALLENGE_TYPE.PLAYER2_FINISH
                if not 'replay' in game['player1'] and not 'replay' in game['player2']:
                    challenge.state = CHALLENGE_TYPE.OPEN_GAME
                if game['player1'] is not None and game['player2'] is not None:
                    if 'replay' in game['player1'] and 'replay' in game['player2']:
                        challenge.state = CHALLENGE_TYPE.BOTH_PLAYERS_FINISH

                        # Update players with earnings
                        player1 = None
                        player2 = None
                        opponents = None
                        racewinnings = None
                        winner = 'draw'

                        player1 = Player.getplayerByFbid(self, challenge.uid1)
                        if player1 is None:
                            player1 = Player.getplayer(self, challenge.uid1)

                        if player1 is not None:
                            player2 = Player.getplayerByFbid(self, challenge.uid2)
                            if player2 is None:
                                player2 = Player.getplayer(self, challenge.uid2)

                        if player2 is not None:
                            racewinnings = Data.getDataAsObj(self, 'racewinnings', config.data_version['racewinnings'])

                        if racewinnings is not None:
                            opponents = Data.getDataAsObj(self, 'opponent_en', config.data_version['opponent'])

                        # everything is good - we have 2 player models and the winnings data
                        if opponents is not None:
                            prize1 = 0
                            prize2 = 0

                            # only use the first one for multiplayer challenges
                            win_prize = opponents.obj[challenge.track][0]['win_prize']
                            lose_prize = opponents.obj[challenge.track][0]['lose_prize']

                            if game['player1']['laptime'] < game['player2']['laptime']:        # player1 wins
                                winner = 'player1'
                                prize1 = win_prize
                                prize2 = lose_prize
                                player1.state_obj['total_wins'] += 1
                            elif game['player1']['laptime'] > game['player2']['laptime']:
                                winner = 'player2'
                                prize1 = lose_prize
                                prize2 = win_prize
                                player2.state_obj['total_wins'] += 1
                            else:
                                winner = 'draw'
                                prize1 = lose_prize
                                prize2 = lose_prize


                            player2.state_obj['cash'] += prize2
                            if uid == challenge.uid2:
                                player2.info_obj['updated'] = start_time
                            if Player.setplayer(self, player2):
                                logging.info('player2 saved')

                            player1.state_obj['total_races'] += 1
                            player2.state_obj['total_races'] += 1

                            challenge.state = CHALLENGE_TYPE.GAME_OVER
                            game['result'] = {'winner': winner, 'player1_prize': prize1, 'player2_prize': prize2,
                                              'player1_seen': uid == challenge.uid1, 'player2_seen': uid == challenge.uid2}

                _upd = True

            elif game['result']['player1_seen'] is False or game['result']['player2_seen'] is False:
                if uid == challenge.uid1:
                    game['result']['player1_seen'] = True
                    _upd = True
                if uid == challenge.uid2:
                    game['result']['player2_seen'] = True
                    _upd = True

                challenge.manual_update = True

            logging.debug("Update finished with state " + challenge.state + " type = " + type)
            if _upd is True:
                challenge.data = json.dumps(game)
                if challenge.put():
                    # TODO : memcache replace
                    memcache.delete(config.db['challengedb_name'] + '.' + challenge.id)
                    if not memcache.add(config.db['challengedb_name'] + '.' + challenge.id, challenge):
                        logging.warning('Challenge - Set memcache for challenge by Id failed!')

        else:
            self.error = 'Challenge ID=' + chid + ' could not be found.'
            logging.debug(self.error)

        return challenge

    @staticmethod
    def DeleteById(self, chid):
        """ Parameters:
            chid - Challenge Id
        """
        challenge = memcache.get(config.db['challengedb_name'] + '.' + chid)
        if challenge is None:
            challenges = Challenge.all().filter('id =', chid).filter('state !=',
                                                                     CHALLENGE_TYPE.BOTH_PLAYERS_FINISH).ancestor(
                db.Key.from_path('Challenge', config.db['challengedb_name'])).fetch(1)
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
        challenging = Challenge.all().filter('uid1 =', uid).ancestor(
            db.Key.from_path('Challenge', config.db['challengedb_name']))
        if challenging is not None:
            for challenge in challenging:
                challenge.delete()
                deleted = True
        challengers = Challenge.all().filter('uid2 =', uid).ancestor(
            db.Key.from_path('Challenge', config.db['challengedb_name']))
        if challengers is not None:
            for challenge in challengers:
                challenge.delete()
                deleted = True
        return deleted

    # TODO: Need to test if this date filter works..
    @staticmethod
    def PurgeOldChallenges(self):
        challenges = Challenge.all().filter('created <', datetime.now() - timedelta(days=7)).ancestor(
            db.Key.from_path('Challenge', config.db['challengedb_name'])).fetch(1)
        if challenges is not None:
            logging.warning('Deleting ' + challenges)
            challenges.delete()

    #returns everything except replay data
    @staticmethod
    def ComposeChallenges(self, player):
        self.respn += '"version":"alpha","challenges":{"challengers":['
        challengers = Challenge.GetChallengers(self, player.fbid)

        #TODO remove this nasty =='[]' - not very pythonic. Need to find a proper way of finding empty or null dicts
        if challengers is None or list(challengers) == [] or list(challengers) == '[]':
            logging.debug('ComposeChallenges getting uuid ' + player.uuid)
            challengers = Challenge.GetChallengers(self, player.uuid)
        if challengers is not None:

            logging.debug('ComposeChallenges: challengers is not None:')
            for _challenge in challengers:
                logging.debug('ComposeChallenges found challenge')
                _gameObj = json.loads(_challenge.data)
                self.respn += '{'
                self.respn += '"chid":"' + _challenge.id + '",'
                self.respn += '"uidx":"' + _challenge.uid1 + '",'
                self.respn += '"track":"' + _challenge.track + '",'
                self.respn += '"state":"' + _challenge.state + '",'
                if _gameObj['player1'] is not None:
                    #self.respn += '"laptime":' + str(_gameObj['player1']['laptime']) + ','
                    #self.respn += '"cardata":"' + str(_gameObj['player1']['cardata']) + '",'
                    self.respn += '"name":"' + str(_gameObj['player1']['name']) + '",'
                    self.respn += '"image":"' + str(_gameObj['player1']['image']) + '"'
                    #self.respn += '"created":"' + str(_gameObj['player1']['created']) + '"'
                self.respn += '},'
        self.respn = self.respn.rstrip(',') + '],"challenging":['

        challenging = Challenge.GetChallenging(self, player.uuid)
        if challenging is None:
            challenging = Challenge.GetChallenging(self, player.fbid)
        if challenging is not None:
            for _challenge in challenging:
                _gameObj = json.loads(_challenge.data)
                self.respn += '{'
                self.respn += '"action":"getplayerdata",'
                self.respn += '"chid":"' + _challenge.id + '",'
                self.respn += '"uidx":"' + _challenge.uid2 + '",'
                self.respn += '"track":"' + _challenge.track + '",'
                self.respn += '"state":"' + _challenge.state + '",'
                if _gameObj['player2'] is not None:
                    #self.respn += '"laptime":' + str(_gameObj['player1']['laptime']) + ','
                    #self.respn += '"cardata":"' + str(_gameObj['player1']['cardata']) + '",'
                    self.respn += '"name":"' + str(_gameObj['player2']['name']) + '",'
                    self.respn += '"image":"' + str(_gameObj['player2']['image']) + '"'
                    #self.respn += '"created":"' + str(_gameObj['player2']['created']) + '"'
                self.respn += '},'
        self.respn = self.respn.rstrip(',') + '],"completed":['
        completed = Challenge.GetCompleted(self, player.uuid)
        if completed is None:
            completed = Challenge.GetCompleted(self, player.fbid)
        if completed is not None:
            for _challenge in completed:
                _gameObj = json.loads(_challenge.data)
                self.respn += '{'
                self.respn += '"chid":"' + _challenge.id + '",'
                self.respn += '"track":"' + _challenge.track + '",'
                self.respn += '"state":"' + _challenge.state + '",'
                #self.respn += '"uidx":"'+_challenge.uid1+'",'
                if player.fbid == _challenge.uid1 or player.uuid == _challenge.uid1:
                    self.respn += '"uidx":"' + _challenge.uid2 + '",'
                    if _gameObj['player2'] is not None:
                        #self.respn += '"laptime":' + str(_gameObj['player2']['laptime']) + ','
                        #self.respn += '"cardata":"' + str(_gameObj['player2']['cardata']) + '",'
                        self.respn += '"name":"' + str(_gameObj['player2']['name']) + '",'
                        self.respn += '"image":"' + str(_gameObj['player2']['image']) + '"'
                        #self.respn += '"created":"' + str(_gameObj['player2']['created']) + '"'
                    self.respn += '}'
                else:
                    self.respn += '"uidx":"' + _challenge.uid1 + '",'
                    if _gameObj['player1'] is not None:
                        #self.respn += '"laptime":' + str(_gameObj['player1']['laptime']) + ','
                        #self.respn += '"cardata":"' + str(_gameObj['player1']['cardata']) + '",'
                        self.respn += '"name":"' + str(_gameObj['player1']['name']) + '",'
                        self.respn += '"image":"' + str(_gameObj['player1']['image']) + '"'
                        #self.respn += '"created":"' + str(_gameObj['player1']['created']) + '"'
                    self.respn += '}'
            self.respn += ']}'
        logging.debug(self.respn)
        return self.respn

    # Returns replay data also
    @staticmethod
    def ComposeActualChallenge(self, challenge):
        self.respn += '"info":{'
        self.respn += '"id":"' + challenge.id + '",'
        self.respn += '"track":"' + challenge.track + '",'
        self.respn += '"uid1":"' + challenge.uid1 + '",'
        self.respn += '"uid2":"' + challenge.uid2 + '",'
        self.respn += '"state":"' + challenge.state + '",'
        self.respn += '"created":"' + str(challenge.created) + '"'
        self.respn += '},"game":' + challenge.data
        return self.respn