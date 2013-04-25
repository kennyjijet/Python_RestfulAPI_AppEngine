import webapp2

from google.appengine.api import urlfetch

class Push(webapp2.RequestHandler):
	def get(self): 
		if self.request.get('url'):
			result = urlfetch.fetch(self.request.get('url'))
			if result.status_code == 200:
				data = result.content
		else:
			data = '"error":"url is required"}'
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(data)