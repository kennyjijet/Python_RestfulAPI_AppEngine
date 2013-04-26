import time

# built-in libraries
from random 		import randint
from datetime		import datetime

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
			now = datetime.now()
			return now.strftime('%S%y%M%m%H%d')+str(randint(1, 100))

	@staticmethod
	def genitemid(self):		
		now = datetime.now()
		return now.strftime('item%S%y%M%m%H%d')+str(randint(1, 100))
		
	@staticmethod
	def RESTreturn(self, time_taken):
		self.debug += '('+str(time_taken)+')'
		if self.respn == '': 
			self.respn = '""'
		else:
			if (self.respn[0] != '{' or self.respn[len(self.respn)-1] != '}') and (self.respn[0] != '[' or self.respn[len(self.respn)-1] != ']') and (self.respn[0] != '"' or self.respn[len(self.respn)-1] != '"'):
				self.respn = '"'+self.respn+'"' 
		self.sinfo = '{"currentTime":'+str(time.time())+'}'
		if self.request.get('debug'):
			return '{"serverInfomation":'+self.sinfo+',"response":'+self.respn+',"error":"'+self.error+'", "debug":"'+self.debug+'"}'
		else:
			return '{"serverInfomation":'+self.sinfo+',"response":'+self.respn+',"error":"'+self.error+'"}'