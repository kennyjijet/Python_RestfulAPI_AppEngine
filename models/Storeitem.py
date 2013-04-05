from google.appengine.ext import db
	
class Storeitem(db.Model):
	version 			= db.StringProperty()
	data 				= db.TextProperty()
	created				= db.DateTimeProperty(auto_now_add=True)