""" finishresearch action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae


	Description
	---------------------------------------------------------------
	I am an API to fast track finish research


	Input:
	---------------------------------------------------------------
	required: passwd, uuid, inid
	optional: version


	Output:
	---------------------------------------------------------------
	updated with deducted gold and finished research info


"""

# built-in libraries
import webapp2
import logging
import time
import math

# config
from config import config

# include
from helpers.utils import Utils
from models.Data import Data
from models.Player import Player
from models.Research import Research

# class implementation
class finishresearch(webapp2.RequestHandler):

	# standard variables
	sinfo = ''
	respn = ''
	error = ''
	debug = ''

	# get function implementation
	def get(self):
		# reset/clean standard variables
		Utils.reset(self)

		# validate and assign parameters
		passwd = Utils.required(self, 'passwd')
		version = config.data_version['buildings']
		if self.request.get('version'):
			version = self.request.get('version')
		uuid = Utils.required(self, 'uuid')
		inid = Utils.required(self, 'inid')

		# start count
		start_time = time.time()

		# set default parameters
		player = None
		researches = None
		myresearch = None
		economy = None


		# if error, skip this
		if self.error == '':
			player = Player.getplayer_as_obj(self, uuid)

		# if error or player is not, then skip to the end
		if self.error == '' and player is not None:
			researches = Data.getresearches(self, version)

		if self.error == '' and researches is not None:
			myresearch = Research.getmyresearch(self, uuid, inid)

		# if any error or myresearch is none, then skip to the end
		if self.error == '' and myresearch is not None:
			if myresearch.status != Research.ResearchStatus.PENDING:
				self.respn = '{"warning":"research='+inid+' has been finished."}'
			else:
				economy = Data.getDataAsObj(self, 'economy', config.data_version['economy'])

		if self.error == '' and self.respn == '' and economy is not None:
			_name = str(myresearch.itid)
			_pos = myresearch.itid.find('.', len(myresearch.itid)-4)
			_bui = myresearch.itid[0:_pos]
			_lev = myresearch.itid[_pos+1:len(myresearch.itid)]
			_upd = False
			time_left = researches.as_obj[_bui][_lev]['wait'] - int((start_time - myresearch.timestamp)/60)
			if myresearch.status == Research.ResearchStatus.PENDING:
				if time_left > 0:
					sele = economy.obj[0]
					for list in economy.obj:
						logging.info(str(time_left)+' > '+str(list['time_in_minutes']))
						if time_left >= list['time_in_minutes']:
							sele = list
						else:
							logging.info('--->break')
							break
					logging.info(str(sele['time_in_minutes'])+'==>'+str(sele['gold_value']))
					if player.state_obj['gold'] >= sele['gold_value']:
						player.state_obj['gold'] -= sele['gold_value']
						myresearch.status = Research.ResearchStatus.REWARD
						_upd = True
						Player.setplayer_as_obj(self, player)
					else:
						self.respn = '{"warning":"not enough gold!"}'
				else:
					myresearch.status = Research.ResearchStatus.REWARD
					_upd = True

			if _upd is True:
				Research.setmyresearch(self, myresearch)

			if self.error == '' and self.respn == '':
				self.respn = '{"state":'+player.state+', "buildings":['
				self.respn = Research.compose_myresearch(self.respn, myresearch)
				self.respn = self.respn.rstrip(',') + ']'
				self.respn += '}'

		# calculate time taken and return the result
		time_taken = time.time() - start_time
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))

		# do exactly as get() does
	def post(self):
		self.get()