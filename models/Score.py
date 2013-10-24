from google.appengine.ext import db
import logging
import json

# config
from config import config

# include
from models.Data import Data


class Score(db.Model):
    uuid = db.StringProperty()
    type = db.StringProperty()
    point = db.FloatProperty()
    data = db.TextProperty()

    """
    Data takes the format   {"player1":{"start_bonus":[0.1,0.2,0.4],"shift_bonus":[0.2,0.5,0.8],"drift_bonus":[0.3,0.1,0.9],"laptime":30},player2:{..}}
    """

    @staticmethod
    def calculate(self, events, events2, laptime, laptime2):
        # calculate score by linking replay times Race Winnings Data

        racewinnings = Data.getDataAsObj(self, 'racewinnings_en', config.data_version['racewinnings']).obj
        if racewinnings is None:
            racewinnings = Score.GetDefaultRaceWinnings()

        if racewinnings is not None:
            logging.debug("racewinnings: "+json.dumps(racewinnings))

        prize_winner = 1000
        prize_looser = 200

        scorings = [{'player_events': json.loads(events), 'prizes': {}, 'total': 0.0},
                    {'player_events': json.loads(events2), 'prizes': {}, 'total': 0.0}]

        scorings[0]['prize'] = scorings[0]['total'] = prize_winner if ( laptime < laptime2 ) else prize_looser
        scorings[1]['prize'] = scorings[1]['total'] = prize_winner if ( laptime2 < laptime ) else prize_looser

        # initialize all scores to zero
        for _player in scorings:
            for _event_type in _player['player_events']:
                _player['prizes'][_event_type] = 0.0

        logging.debug('Calculating score with ' + json.dumps(scorings))

        for _player in scorings:
            for _event_type in _player['player_events']:
                for _event in _player['player_events'][_event_type]: #floats
                    for _threshold in racewinnings:
                        if abs(_event) < _threshold['timing']:
                            _player['prizes'][_event_type] += int(_player['prize'] * _threshold[_event_type])
                            _player['total'] += _player['prizes'][_event_type]

        return scorings

    @staticmethod
    def GetDefaultRaceWinnings():
        return [{"timing": 0.1, "start_bonus": 0.16, "shift_bonus": 0.16, "drift_bonus": 0.16,
                 "start_message": "Excellent Start", "shift_message": "Excellent Shift",
                 "drift_message": "Excellent Drift"},
                {"timing": 0.2, "start_bonus": 0.08, "shift_bonus": 0.08, "drift_bonus": 0.08,
                 "start_message": "Great Start", "shift_message": "Great Shift",
                 "drift_message": "Great Drift"},
                {"timing": 0.4, "start_bonus": 0.04, "shift_bonus": 0.04, "drift_bonus": 0.04,
                 "start_message": "Good Start", "shift_message": "Good Shift",
                 "drift_message": "Good Drift"},
                {"timing": 0.8, "start_bonus": 0.02, "shift_bonus": 0.02, "drift_bonus": 0.02,
                 "start_message": "Ok Start", "shift_message": "Ok Shift", "drift_message": "Ok Drift"}]

    @staticmethod
    def GetDefaultOpponents():
        return '{"track.1":[{"track_id":"track.1","id":"oppt.1","default_upgrades":"chassis.x3,bodykit.standard.x3,clutch.1,tires.1,intake.1,flywheel.1,turbo.1,body.1,engine.20d,d.spoke.355m,paint.jet.black,accessory.none","1_star_time":0,"2_star_time":2,"3_star_time":4,"win_prize":500,"lose_prize":50,"title":"TIMO GLOCK","description":"I will take you down! To Chinatown! For some Dim Sum!","win_quote":"oppt.1.win","lose_quote":"oppt.1.lose","image":"Textures/profile-opponent-1.png","data":"test1"},{"track_id":"track.1","id":"oppt.2","default_upgrades":"chassis.x5,bodykit.standard.x5,clutch.1,tires.1,intake.1,flywheel.1,turbo.1,body.1,engine.25d,s.spoke.258,paint.jet.black,accessory.none","1_star_time":0,"2_star_time":2,"3_star_time":4,"win_prize":1000,"lose_prize":100,"title":"BRUNO SPENGLE","description":"I will take you down! To Little India! For a Chicken Korma!","win_quote":"oppt.2.win","lose_quote":"oppt.2.lose","image":"Textures/profile-opponent-2.png","data":"test2"},{"track_id":"track.1","id":"oppt.3","default_upgrades":"chassis.x6,bodykit.standard.x6,clutch.1,tires.1,intake.1,flywheel.1,turbo.1,body.1,engine.30d,y.spoke.308,paint.jet.black,accessory.none","1_star_time":0,"2_star_time":2,"3_star_time":4,"win_prize":1500,"lose_prize":150,"title":"MARTIN TOMCZYK","description":"My middle name is Shift! My Maiden name is Drift! Im a proper Shift Drifter!","win_quote":"oppt.3.win","lose_quote":"oppt.3.lose","image":"Textures/profile-opponent-3.png","data":"test3"}],"track.2":[{"track_id":"track.2","id":"oppt.4","default_upgrades":"chassis.x3,bodykit.standard.x3,clutch.1,tires.1,intake.1,flywheel.1,turbo.1,body.1,engine.20d,d.spoke.355m,paint.jet.black,accessory.none","1_star_time":0,"2_star_time":2,"3_star_time":4,"win_prize":1000,"lose_prize":100,"title":"TIMO GLOCK","description":"I will take you down! To Chinatown! For some Dim Sum!","win_quote":"oppt.1.win","lose_quote":"oppt.1.lose","image":"Textures/profile-opponent-1.png","data":"test4"},{"track_id":"track.2","id":"oppt.4","default_upgrades":"chassis.x5,bodykit.standard.x5,clutch.1,tires.1,intake.1,flywheel.1,turbo.1,body.1,engine.25d,s.spoke.258,paint.jet.black,accessory.none","1_star_time":0,"2_star_time":2,"3_star_time":4,"win_prize":1500,"lose_prize":150,"title":"BRUNO SPENGLE","description":"I will take you down! To Little India! For a Chicken Korma!","win_quote":"oppt.2.win","lose_quote":"oppt.2.lose","image":"Textures/profile-opponent-2.png","data":"test5"},{"track_id":"track.2","id":"oppt.5","default_upgrades":"chassis.x6,bodykit.standard.x6,clutch.1,tires.1,intake.1,flywheel.1,turbo.1,body.1,engine.30d,y.spoke.308,paint.jet.black,accessory.none","1_star_time":0,"2_star_time":2,"3_star_time":4,"win_prize":2000,"lose_prize":200,"title":"MARTIN TOMCZYK","description":"My middle name is Shift! My Maiden name is Drift! Im a proper Shift Drifter!","win_quote":"oppt.3.win","lose_quote":"oppt.3.lose","image":"Textures/profile-opponent-3.png","data":"test6"}],"track.3":[{"track_id":"track.3","id":"oppt.6","default_upgrades":"chassis.x3,bodykit.standard.x3,clutch.1,tires.1,intake.1,flywheel.1,turbo.1,body.1,engine.20d,d.spoke.355m,paint.jet.black,accessory.none","1_star_time":0,"2_star_time":2,"3_star_time":4,"win_prize":1500,"lose_prize":150,"title":"TIMO GLOCK","description":"I will take you down! To Chinatown! For some Dim Sum!","win_quote":"oppt.1.win","lose_quote":"oppt.1.lose","image":"Textures/profile-opponent-1.png","data":"test7"},{"track_id":"track.3","id":"oppt.7","default_upgrades":"chassis.x5,bodykit.standard.x5,clutch.1,tires.1,intake.1,flywheel.1,turbo.1,body.1,engine.25d,s.spoke.258,paint.jet.black,accessory.none","1_star_time":0,"2_star_time":2,"3_star_time":4,"win_prize":2000,"lose_prize":200,"title":"BRUNO SPENGLE","description":"I will take you down! To Little India! For a Chicken Korma!","win_quote":"oppt.2.win","lose_quote":"oppt.2.lose","image":"Textures/profile-opponent-2.png","data":"test8"},{"track_id":"track.3","id":"oppt.8","default_upgrades":"chassis.x6,bodykit.standard.x6,clutch.1,tires.1,intake.1,flywheel.1,turbo.1,body.1,engine.30d,y.spoke.308,paint.jet.black,accessory.none","1_star_time":0,"2_star_time":2,"3_star_time":4,"win_prize":2500,"lose_prize":250,"title":"MARTIN TOMCZYK","description":"My middle name is Shift! My Maiden name is Drift! Im a proper Shift Drifter!","win_quote":"oppt.3.win","lose_quote":"oppt.3.lose","image":"Textures/profile-opponent-3.png","data":"test9"}],"track.4":[{"track_id":"track.4","id":"oppt.9","default_upgrades":"chassis.x3,bodykit.standard.x3,clutch.1,tires.1,intake.1,flywheel.1,turbo.1,body.1,engine.20d,d.spoke.355m,paint.jet.black,accessory.none","1_star_time":0,"2_star_time":2,"3_star_time":4,"win_prize":2000,"lose_prize":200,"title":"TIMO GLOCK","description":"I will take you down! To Chinatown! For some Dim Sum!","win_quote":"oppt.1.win","lose_quote":"oppt.1.lose","image":"Textures/profile-opponent-1.png","data":"test10"},{"track_id":"track.4","id":"oppt.10","default_upgrades":"chassis.x5,bodykit.standard.x5,clutch.1,tires.1,intake.1,flywheel.1,turbo.1,body.1,engine.25d,s.spoke.258,paint.jet.black,accessory.none","1_star_time":0,"2_star_time":2,"3_star_time":4,"win_prize":2500,"lose_prize":250,"title":"BRUNO SPENGLE","description":"I will take you down! To Little India! For a Chicken Korma!","win_quote":"oppt.2.win","lose_quote":"oppt.2.lose","image":"Textures/profile-opponent-2.png","data":"test11"},{"track_id":"track.4","id":"oppt.11","default_upgrades":"chassis.x6,bodykit.standard.x6,clutch.1,tires.1,intake.1,flywheel.1,turbo.1,body.1,engine.30d,y.spoke.308,paint.jet.black,accessory.none","1_star_time":0,"2_star_time":2,"3_star_time":4,"win_prize":3000,"lose_prize":300,"title":"MARTIN TOMCZYK","description":"My middle name is Shift! My Maiden name is Drift! Im a proper Shift Drifter!","win_quote":"oppt.3.win","lose_quote":"oppt.3.lose","image":"Textures/profile-opponent-3.png","data":"test12"}]}'
