""" noaction action class

	Project: GrandCentral-GAE
	Author: Plus Pingya
	Github: https://github.com/Gamepunks/grandcentral-gae


	Description
	---------------------------------------------------------------
	I am an API to handle an unknown action calls

"""

# built-in libraries
import webapp2
import json

# class implementation
class noactions(webapp2.RequestHandler):

    # get function implementation
	def get(self):

        # response with error message,
		result = {
			"error":	"No such an action were found, please contact admin!",
			"response":	""
		}
		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(json.dumps(result))

	# do exactly as get() does
	def post(self):
		self.get()