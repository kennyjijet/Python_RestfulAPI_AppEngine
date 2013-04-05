import webapp2
import json

class noactions(webapp2.RequestHandler):

	def get(self):
		result = {
			"error":	"No such an action were found, please contact admin!",
			"response":	""
		}
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(json.dumps(result))
		
	def post(self):
		self.get()