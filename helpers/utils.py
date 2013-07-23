import time
import json
import uuid

# config
from config import config
# built-in libraries
from random import randint
from datetime import datetime

class Utils(object):

	@staticmethod
	def reset(self):
		self.sinfo = ''
		self.respn = ''
		self.error = ''
		self.debug = ''
		
	@staticmethod
	def required(self, par_name):
		if self.error == "":
			if self.request.get(par_name):
				return self.request.get(par_name)
			else: 
				self.error = par_name + " is a required parameter."
		return "undefined"
		
	@staticmethod
	def geneuuid(self, par_name):
		if self.request.get(par_name):
			return self.request.get(par_name)
		else:
			#now = datetime.now()
			return 'uuid-'+str(uuid.uuid4()) #now.strftime('%m%H%d')+str(randint(1, 1000000))

	@staticmethod
	def genitemid(self):		
		#now = datetime.now()
		return 'item-'+str(uuid.uuid4()) #now.strftime('item%m%H%d')+str(randint(1, 1000000))

	@staticmethod
	def genanyid(self, any):
		#now = datetime.now()
		return any+'-'+str(uuid.uuid4()) #now.strftime(str(any)+'%m%H%d')+str(randint(1, 1000000))
			
	@staticmethod
	def RESTreturn(self, time_taken):
		stampNow = int(time.time())
		self.debug += '('+str(time_taken)+')'
		if self.respn == '': 
			self.respn = '""'
		else:
			if (self.respn[0] != '{' or self.respn[len(self.respn)-1] != '}') and (self.respn[0] != '[' or self.respn[len(self.respn)-1] != ']') and (self.respn[0] != '"' or self.respn[len(self.respn)-1] != '"'):
				self.respn = '"'+self.respn+'"' 
		self.sinfo = '{"serverName":"'+config.server['serverName']+'","apiVersion":'+str(config.server['apiVersion'])+',"requestDuration":'+str(time_taken)+',"currentTime":'+str(stampNow)+'}'
		if self.request.get('debug'):
			return '{"serverInformation":'+self.sinfo+',"response":'+self.respn+',"error":"'+self.error+'", "debug":"'+self.debug+'"}'
		else:
			return '{"serverInformation":'+self.sinfo+',"response":'+self.respn+',"error":"'+self.error+'"}'