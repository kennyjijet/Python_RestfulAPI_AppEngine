from google.appengine.ext import db

class Player(db.Model):
	uuid 		= db.StringProperty()
	state 		= db.TextProperty()
	updated		= db.DateTimeProperty(auto_now_add=True)