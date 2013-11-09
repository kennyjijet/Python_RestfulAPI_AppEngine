""" getdata action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae


	Description
	---------------------------------------------------------------
	I am an API to get game data(s) (Data deployed from Google Drive
	Custom Backend


	Input:
	---------------------------------------------------------------
	required: passwd, type,
	optional: version, lang


	Output:
	---------------------------------------------------------------
	requested game data(s)


"""

# built-in libraries
import webapp2

# config

# include
from helpers.utils import Utils

# class implementation
class force500(webapp2.RequestHandler):
    # standard variables
    game = ''
    sinfo = ''
    respn = ''
    error = ''
    debug = ''

    # get function implementation
    def get(self):
        self.response.set_status(500)


    # do exactly as get() does
    def post(self):
        self.get()