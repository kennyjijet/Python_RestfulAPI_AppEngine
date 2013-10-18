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

# class implementation
class finishrace(webapp2.RequestHandler):
    description = "I am an API to finish a race and reward the player with gold"
    output = "player state object"
    # standard variables
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

        logging.debug(
            '/finishrace?uuid=' + uuid + '&uuid2=' + uuid2 + '&events=' + events + '&events2=' + events2 + '&laptime=' + laptime + '&laptime2=' + laptime2)

        # check password
        if self.error == '' and passwd != config.testing['passwd']:
            self.error = 'passwd is incorrect.'

        start_time = time.time()                                                # start count

        # if error, skip this
        #if self.error != '' or self.error is None:
        player = Player.getplayer(self, uuid)
        player2 = Player.getplayer(self, uuid2)
        ai = None
        # TODO: move this from AR language to default or UK
        if player2 is None:
            data = Data.getDataAsObj(self, 'opponent_ar', 1.0)
            if data is None:
                opponents = {'obj': json.loads(Score.GetDefaultOpponents())}
            else:
                opponents = data.obj

            for track in opponents:
                for opponent in opponents[track]:
                    if opponent['id'] == uuid2:
                        ai = opponent
                        self.error = ''

        if player is not None and guid != '':
            if guid != player.state_obj['guid']:
                player = None
                self.error = config.error_message['dup_login']

        if player is not None:
            scores = Score.calculate(self, events, events2, laptime, laptime2)

            if scores is not None:
                player.state_obj['cash'] += scores[0]['total']
                player.state_obj['updated'] = start_time
                if player2 is not None:
                    player.state_obj[GCVars.total_races] += 1
                    if laptime < laptime2:
                        player.state_obj[GCVars.total_wins] += 1

                if ai is not None:
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
                        difference = float(laptime) - float(laptime2)
                        results = {}
                        star_value = 0
                        new_star_value = 0
                        if player.state_obj.has_key('results'):
                            results = json.loads(player.state_obj['results'])
                        if results.has_key(uuid2):
                            star_value = int(results[uuid2])

                        if difference < float(ai['1_star_time']):
                            new_star_value = 1
                        if difference < float(ai['2_star_time']):
                            new_star_value = 2
                        if difference < float(ai['3_star_time']):
                            new_star_value = 3

                        if new_star_value > star_value:
                            results[uuid2] = new_star_value

                        player.state_obj.setdefault('results', json.dumps(results))

                Player.setplayer(self, player)
                player_score = scores[0];
                scores_to_return = {
                    'score_prize': player_score['prize'],
                    'score_drift': player_score['prizes']['drift_bonus'],
                    'score_shift': player_score['prizes']['shift_bonus'],
                    'score_start': player_score['prizes']['start_bonus']
                }

                logging.debug('finishrace player state:' + player.state)
                self.respn = '{"state":' + player.state + ',"scores":' + json.dumps(scores_to_return) + '}'

                if player2 is not None:
                    player2.state_obj[GCVars.cash] += scores[1]['total']
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
