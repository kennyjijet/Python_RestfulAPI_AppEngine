import webapp2
import json
import logging
import time

logging.basicConfig(filename='exam.log', level=logging.INFO)

# config
from config			import config

# include
from helpers.utils 		import Utils
from controllers.Core 	import Core


class behaviour():

	@staticmethod
	def reward(self, prms):
		params = prms.split(',')
		if len(params) != 3:
			self.error = 'Reward event receieved invalid parameter(s)! example: uuid #,resource,@amount'
		else:
			self.error = ''
			player = Core.getplayer_as_obj(self, params[0])
		if self.error == '' and player is not None:
			player.state_obj[params[1]] += int(params[2])
			Core.setplayer_as_obj(self, player)
			Utils.compose_player(self, player)
			
	@staticmethod
	def deduct(self, prms):
		params = prms.split(',')
		if len(params) != 3:
			self.error = 'Deduct event receieved invalid parameter(s)! example: uuid #,resource,@amount'
		else:
			self.error = ''
			player = Core.getplayer_as_obj(self, params[0])
		if self.error == '' and player is not None:
			player.state_obj[params[1]] -= int(params[2])
			Core.setplayer_as_obj(self, player)
			Utils.compose_player(self, player)
	
	@staticmethod
	def collect(self, prms):
		params = prms.split(',')
		if len(params) != 4:
			self.error = 'Collect event receieved invalid parameter(s)! eg: uuid,itid'
		else:
			self.error = ''
			player = Core.getplayer_as_obj(self, params[0])
			item = Core.getspecificinidproduceditem(self, params[0], params[1])
		if player is not None and item is not None:
			storeitem = Core.getstoreitem_as_obj(self)
			player.state_obj[params[3]] += int(storeitem[item.itid]['resource_units'])
			item.status = 'rewarded'
			item.timestamp = time.time() + storeitem[item.itid]['time'] * 3600
			if item.put():
				Core.setplayer_as_obj(self, player)
				Utils.compose_player(self, player)
			else:
				self.error = 'event: unable to update item!'
		else:
			self.respn = '{"warning":"no item has resource produced!"}'
		
		
class event(webapp2.RequestHandler):
	
	sinfo = ''
	respn = ''
	error = ''
	debug = ''
	
	def get(self):
		Utils.reset(self)
		
		# validate
		passwd = Utils.required(self, 'passwd')
		evid = Utils.required(self, 'evid')
		prms = Utils.required(self, 'prms')

		if self.error == '' and passwd != config.testing['passwd']:
			self.error = 'passwd is incorrect.'
			
		start_time = time.time()
		
		if self.error == '':
			events = Core.getevents_as_obj(self, str(config.server['apiVersion']))
			self.error = 'event ' + evid + ' does not exist!'
			if events is not None:
				for event in events:
					if event['id'] == evid:
						params = prms
						for item in event:
							if "parameter" in str(item) and event[item] != '':
								params += ','+str(event[item])
						getattr(behaviour, event['behaviour'])(self, params)
						
		# return
		time_taken =  time.time() - start_time;
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(Utils.RESTreturn(self, time_taken))
		
		
	def post(self):
		self.get()