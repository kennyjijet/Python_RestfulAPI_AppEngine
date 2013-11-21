# built-in libraries
import webapp2
import logging
import time
import json

# config
from config import config
from GCVars import GCVars

# include
from helpers.utils import Utils
from models.Player import Player
from models.Score import Score
from models.Data import Data
from models.Building import Building

# class implementation
class finishrace(webapp2.RequestHandler):
    description = "I am an API to finish a race and reward the player with gold"
    output = "player state object"
    # standard variables
    game = ''
    sinfo = ''
    respn = ''
    error = ''
    debug = ''

    # get function implementation
    def get(self):
        Utils.reset(self)                                                        # reset/clean standard variables

        # validate and assign parameters
        passwd = Utils.required(self, GCVars.passwd)
        guid = self.request.get('guid')
        uuid = Utils.required(self, 'uuid')
        uuid2 = Utils.required(self, 'uid2')
        events = Utils.required(self, 'events')
        events2 = Utils.required(self, 'events2')
        laptime = Utils.required(self, 'laptime')
        laptime2 = Utils.required(self, 'laptime2')
        track = Utils.required(self, 'track')

        version = config.data_version['building']
        if self.request.get('version'):
            version = self.request.get('version')
        lang = config.server["defaultLanguage"]
        if self.request.get('lang'):
            lang = self.request.get('lang')

        Utils.LogRequest(self)
        # check password
        if self.error == '' and passwd != config.testing['passwd']:
            self.error = 'passwd is incorrect.'

        start_time = time.time()                                                # start count

        # if error, skip this
        #if self.error != '' or self.error is None:
        player = Player.getplayer(self, uuid)
        player2 = Player.getplayer(self, uuid2)
        ai = None
        my_building = None

        win_prize = None
        lose_prize = None

        data = Data.getDataAsObj(self, 'opponent_en', 1.0)
        if data is None:
            opponents = {'obj': json.loads(Score.GetDefaultOpponents())}
        else:
            opponents = data.obj

        for _track in opponents:
            for opponent in opponents[_track]:
                if not win_prize:
                    win_prize = opponent['win_prize']
                if not lose_prize:
                    lose_prize = opponent['lose_prize']
                if player2 is None:
                    if opponent['id'] == uuid2:
                        ai = opponent
                        self.error = ''

        if player is not None and guid != '':
            if guid != player.state_obj['guid']:
                player = None
                self.error = config.error_message['dup_login']

        if player is not None:
            scores = Score.calculate(self, events, events2, laptime, laptime2, win_prize, lose_prize)

            if scores is not None:
                score = scores[0]['total']
                #player.state_obj['cash'] += score
                player.state_obj['updated'] = start_time


                if player2 is not None:
                    player.state_obj[GCVars.total_races] += 1
                    if laptime < laptime2:
                        player.state_obj[GCVars.total_wins] += 1

                if ai is not None:
                    # save the resource to a building, ready for collection
                    my_building = Building.save_resource_to_building(self, lang, version, player.uuid, track, score)
                    if player.state_obj.has_key(GCVars.total_ai_races):
                        player.state_obj[GCVars.total_ai_races] += 1
                    else:
                        player.state_obj.setdefault(GCVars.total_ai_races, 1)

                    if laptime < laptime2:
                        if player.state_obj.has_key(GCVars.total_ai_wins):
                            player.state_obj[GCVars.total_ai_wins] += 1
                        else:
                            player.state_obj.setdefault(GCVars.total_ai_wins, 1)

                        #find star rating
                        difference = float(laptime2) - float(laptime)
                        data = {}
                        star_value = 0
                        new_star_value = 0
                        if player.state_obj.has_key('data'):
                            data = json.loads(player.state_obj['data'])
                        if data.has_key(uuid2):
                            star_value = int(data[uuid2])

                        #0,2,4 = 1 start time, 2 start time, 3 star time
                        if difference > float(ai['1_star_time']):
                            new_star_value = 1
                        if difference > float(ai['2_star_time']):
                            new_star_value = 2
                        if difference > float(ai['3_star_time']):
                            new_star_value = 3

                        if new_star_value > star_value:
                            data[uuid2] = new_star_value

                        logging.debug(str(new_star_value) + ' > star_value:' + str(star_value) + ', laptime 1:' + str(laptime) + ', laptime2: ' + str(laptime2))
                        logging.debug('setting player data to ' + json.dumps(data))

                        player.state_obj['data'] = json.dumps(data)
                        player.state = json.dumps(player.state_obj)

                Player.setplayer(self, player)
                if 'xxx' in player.state:
                        self.error += '[KNOWN ISSUE] Player car lost. Please visit showroom and buy X1 again.'

                player_score = scores[0]
                scores_to_return = {
                    'score_prize': player_score['prize'],
                    'score_drift': player_score['prizes']['drift_bonus'],
                    'score_shift': player_score['prizes']['shift_bonus'],
                    'score_start': player_score['prizes']['start_bonus']
                }

                logging.debug('finishrace player state:' + player.state)
                self.respn = '{"state":' + player.state
                self.respn += ',"scores":' + json.dumps(scores_to_return)
                if my_building is not None:
                    self.respn += ',"building":['
                    self.respn = Building.compose_mybuilding(self.respn, my_building)
                    self.respn = self.respn.rstrip(',') + ']'
                self.respn += '}'

                if player2 is not None:
                    score = scores[1]['total']
                    #player2.state_obj[GCVars.cash] += score
                    Building.save_resource_to_building(self, lang, version, player2.uuid, track, score)
                    player2.state_obj[GCVars.updated] = start_time
                    player2.state_obj[GCVars.total_races] += 1
                    if laptime2 < laptime:
                        player2.state_obj[GCVars.total_wins] += 1
                    Player.setplayer(self, player2)
        else:
            self.error = 'Cant find a player for ' + uuid
            #else:
        #    logging.warn('final error ' + self.error)

        # calculate time taken and return the result
        time_taken = time.time() - start_time
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(Utils.RESTreturn(self, time_taken))

    # do exactly as get() does
    def post(self):
        self.get()
