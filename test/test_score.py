# built-in libraries
import webapp2
import json
# include
from helpers.utils import Utils
from models.Score import Score

# class implementation
class test_score(webapp2.RequestHandler):
    # standard variables
    game = ''
    sinfo = ''
    respn = ''
    error = ''
    debug = ''

    # get function implementation

    def get(self):
        Utils.reset(self)
        # calculate score by linking replay times Race Winnings Data

        event1 = '{"start_bonus": [0.1, 0.2, 0.4], "shift_bonus": [0.2, 0.5, 0.8], "drift_bonus": [0.3, 0.1, 0.9]}'
        event2 = '{"start_bonus": [0.1, 0.2, 0.4], "shift_bonus": [0.2, 0.5, 0.8], "drift_bonus": [0.3, 0.1, 0.9]}'
        laptime1 = 1
        laptime2 = 2
        self.respn = json.dumps(Score.calculate(self, event1, event2, laptime1, laptime2))
        # calculate time taken and return the result
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(Utils.RESTreturn(self, 1))

    # do exactly as get() does
    def post(self):
        self.get()