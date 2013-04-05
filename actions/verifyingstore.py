import webapp2
import json
import logging
import math
import time
import base64
import urllib2

logging.basicConfig(filename='verifyingstore.log', level=logging.INFO)

# built-in libraries
from random 		import randint
from datetime 		import datetime, date

# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache, urlfetch

# config
from config			import config

# models
from models.Storeitem 	import Storeitem
from models.Player		import Player

class verifyingstore(webapp2.RequestHandler):
	
	error = ''
	respn = ''
	debug = ''
	
	#setup
	
	
	def reset(self):
		self.error = ''
		self.respn = ''
		self.debug = ''
	
	def required(self, par_name):
		if self.error == "": 
			if self.request.get(par_name):
				return self.request.get(par_name)
			else: 
				self.error = par_name + " is a required parameter."
		return "undefined"

	
	def get(self):
	
		self.reset()
		
		# validate
		uuid	= self.required('uuid')
		receipt = self.required('receipt')
		
		start_time = time.time()
		
		if self.error == '':
			_memcache = False
			player = memcache.get(config.db['playerdb_name']+'.'+uuid)
			if player is None:
				players = Player.all().filter('uuid =', uuid).ancestor(db.Key.from_path('Player', config.db['playerdb_name'])).fetch(1);
				if len(players)>=1:
					player = players[0]
				else:
					self.error = 'uuid='+uuid+' was not found.'
					player = None
			else:
				_memcache = True
				
			if player is not None:
				if _memcache==False:
					if not memcache.add(config.db['playerdb_name']+'.'+uuid, player, config.memcache['holdtime']):
						logging.warning('softpurchase - Memcache set player failed')
		
		if self.error == '' and player is not None:	
			
			if self.request.get('sandbox'): 
				url = config.apple['verifyingReceiptSandboxURL']
			else:
				url = config.apple['verifyingReceiptURL']
			
			encoded = base64.b64encode(receipt)
			#form_fields = '{"receipt-data":"'+config.apple['sampleEncodedReceipt']+'"}'
			form_fields = '{"receipt-data":"'+receipt+'"}'
			#form_fields = '{"receipt-data":"ewoJInNpZ25hdHVyZSIgPSAiQW9mVVpzcDI4VVBkVmdjbVN0RFU4WUNRUEY4aVk2V1JyYXRrYmowZlJYVlRBRFVtb0E4UkJHZnRZUTJYVVc0MU1qYVZBYTFFVGRDSTFCV1dXV2RrQUIyR0J2MUpLSTg4Zk1WMW5aSGlDY2FzYy9SS2UvdVdoM0tJOVlWYk5OZGhDN0NrNkM3VkZ0dTRuc2FickdHQVp6cDhXckhWNmtDVjNKREFwMDdiUmxWdUFBQURWekNDQTFNd2dnSTdvQU1DQVFJQ0NHVVVrVTNaV0FTMU1BMEdDU3FHU0liM0RRRUJCUVVBTUg4eEN6QUpCZ05WQkFZVEFsVlRNUk13RVFZRFZRUUtEQXBCY0hCc1pTQkpibU11TVNZd0pBWURWUVFMREIxQmNIQnNaU0JEWlhKMGFXWnBZMkYwYVc5dUlFRjFkR2h2Y21sMGVURXpNREVHQTFVRUF3d3FRWEJ3YkdVZ2FWUjFibVZ6SUZOMGIzSmxJRU5sY25ScFptbGpZWFJwYjI0Z1FYVjBhRzl5YVhSNU1CNFhEVEE1TURZeE5USXlNRFUxTmxvWERURTBNRFl4TkRJeU1EVTFObG93WkRFak1DRUdBMVVFQXd3YVVIVnlZMmhoYzJWU1pXTmxhWEIwUTJWeWRHbG1hV05oZEdVeEd6QVpCZ05WQkFzTUVrRndjR3hsSUdsVWRXNWxjeUJUZEc5eVpURVRNQkVHQTFVRUNnd0tRWEJ3YkdVZ1NXNWpMakVMTUFrR0ExVUVCaE1DVlZNd2daOHdEUVlKS29aSWh2Y05BUUVCQlFBRGdZMEFNSUdKQW9HQkFNclJqRjJjdDRJclNkaVRDaGFJMGc4cHd2L2NtSHM4cC9Sd1YvcnQvOTFYS1ZoTmw0WElCaW1LalFRTmZnSHNEczZ5anUrK0RyS0pFN3VLc3BoTWRkS1lmRkU1ckdYc0FkQkVqQndSSXhleFRldngzSExFRkdBdDFtb0t4NTA5ZGh4dGlJZERnSnYyWWFWczQ5QjB1SnZOZHk2U01xTk5MSHNETHpEUzlvWkhBZ01CQUFHamNqQndNQXdHQTFVZEV3RUIvd1FDTUFBd0h3WURWUjBqQkJnd0ZvQVVOaDNvNHAyQzBnRVl0VEpyRHRkREM1RllRem93RGdZRFZSMFBBUUgvQkFRREFnZUFNQjBHQTFVZERnUVdCQlNwZzRQeUdVakZQaEpYQ0JUTXphTittVjhrOVRBUUJnb3Foa2lHOTJOa0JnVUJCQUlGQURBTkJna3Foa2lHOXcwQkFRVUZBQU9DQVFFQUVhU2JQanRtTjRDL0lCM1FFcEszMlJ4YWNDRFhkVlhBZVZSZVM1RmFaeGMrdDg4cFFQOTNCaUF4dmRXLzNlVFNNR1k1RmJlQVlMM2V0cVA1Z204d3JGb2pYMGlreVZSU3RRKy9BUTBLRWp0cUIwN2tMczlRVWU4Y3pSOFVHZmRNMUV1bVYvVWd2RGQ0TndOWXhMUU1nNFdUUWZna1FRVnk4R1had1ZIZ2JFL1VDNlk3MDUzcEdYQms1MU5QTTN3b3hoZDNnU1JMdlhqK2xvSHNTdGNURXFlOXBCRHBtRzUrc2s0dHcrR0szR01lRU41LytlMVFUOW5wL0tsMW5qK2FCdzdDMHhzeTBiRm5hQWQxY1NTNnhkb3J5L0NVdk02Z3RLc21uT09kcVRlc2JwMGJzOHNuNldxczBDOWRnY3hSSHVPTVoydG04bnBMVW03YXJnT1N6UT09IjsKCSJwdXJjaGFzZS1pbmZvIiA9ICJld29KSW05eWFXZHBibUZzTFhCMWNtTm9ZWE5sTFdSaGRHVXRjSE4wSWlBOUlDSXlNREV6TFRBMExUQTBJREExT2pFME9qVXhJRUZ0WlhKcFkyRXZURzl6WDBGdVoyVnNaWE1pT3dvSkluVnVhWEYxWlMxcFpHVnVkR2xtYVdWeUlpQTlJQ0psWkdReU5EQTVPREF4TkRObFpEWTFZVGM1T0RBelpEVTJabUl3TXpFM05Ea3daRFpqWXpBMklqc0tDU0p2Y21sbmFXNWhiQzEwY21GdWMyRmpkR2x2YmkxcFpDSWdQU0FpTVRBd01EQXdNREEzTURBMk56UTVOQ0k3Q2draVluWnljeUlnUFNBaU1TNHdJanNLQ1NKMGNtRnVjMkZqZEdsdmJpMXBaQ0lnUFNBaU1UQXdNREF3TURBM01EQTJOelE1TkNJN0Nna2ljWFZoYm5ScGRIa2lJRDBnSWpFaU93b0pJbTl5YVdkcGJtRnNMWEIxY21Ob1lYTmxMV1JoZEdVdGJYTWlJRDBnSWpFek5qVXdOemMyT1RFM09EVWlPd29KSW5WdWFYRjFaUzEyWlc1a2IzSXRhV1JsYm5ScFptbGxjaUlnUFNBaU9UYzVRVFkwUWpjdFJUazNSQzAwTWpjNUxUZzNOMFV0TlRBNVFqVkRSakE0TURnMklqc0tDU0p3Y205a2RXTjBMV2xrSWlBOUlDSlFiR0YwYVc1MWJTNHhJanNLQ1NKcGRHVnRMV2xrSWlBOUlDSTJNekV6TVRVNU9ETWlPd29KSW1KcFpDSWdQU0FpWTI5dExtZGhiV1Z3ZFc1cmN5NXphRzl3SWpzS0NTSndkWEpqYUdGelpTMWtZWFJsTFcxeklpQTlJQ0l4TXpZMU1EYzNOamt4TnpnMUlqc0tDU0p3ZFhKamFHRnpaUzFrWVhSbElpQTlJQ0l5TURFekxUQTBMVEEwSURFeU9qRTBPalV4SUVWMFl5OUhUVlFpT3dvSkluQjFjbU5vWVhObExXUmhkR1V0Y0hOMElpQTlJQ0l5TURFekxUQTBMVEEwSURBMU9qRTBPalV4SUVGdFpYSnBZMkV2VEc5elgwRnVaMlZzWlhNaU93b0pJbTl5YVdkcGJtRnNMWEIxY21Ob1lYTmxMV1JoZEdVaUlEMGdJakl3TVRNdE1EUXRNRFFnTVRJNk1UUTZOVEVnUlhSakwwZE5WQ0k3Q24wPSI7CgkiZW52aXJvbm1lbnQiID0gIlNhbmRib3giOwoJInBvZCIgPSAiMTAwIjsKCSJzaWduaW5nLXN0YXR1cyIgPSAiMCI7Cn0="}'
			
			logging.info(encoded + ' / ' + form_fields)

			result = urlfetch.fetch(url=url,
                        payload=form_fields,
                        method=urlfetch.POST,
                        headers={'Content-Type': 'text/json; charset=utf-8'},
						validate_certificate=False)

			if result.status_code == 200: 
				self.respn = result.content

		# return
		time_taken =  time.time() - start_time;
		self.debug += '('+str(time_taken)+')'
		self.response.headers['Content-Type'] = 'text/html'
		if self.respn == '': 
			self.respn = '""'
		else:
			if (self.respn[0] != '{' or self.respn[len(self.respn)-1] != '}') and (self.respn[0] != '[' or self.respn[len(self.respn)-1] != ']') and (self.respn[0] != '"' or self.respn[len(self.respn)-1] != '"'):
				self.respn = '"'+self.respn+'"' 
		if self.request.get('debug'):
			self.response.write('{"response":'+self.respn+',"error":"'+self.error+'", "debug":"'+self.debug+'"}')
		else:
			self.response.write('{"response":'+self.respn+',"error":"'+self.error+'"}')
		
		
	def post(self):
		self.get()