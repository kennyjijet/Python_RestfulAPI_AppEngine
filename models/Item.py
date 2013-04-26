from google.appengine.ext import db
	
class Item(db.Model):
	uuid 			= db.StringProperty()
	type			= db.StringProperty()
	itid 			= db.StringProperty(indexed=False)
	status			= db.FloatProperty()
	created			= db.DateTimeProperty(auto_now_add=True)