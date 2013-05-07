from google.appengine.ext import db
	
class Item(db.Model):
	uuid 			= db.StringProperty()
	itid			= db.StringProperty()
	inid 			= db.StringProperty(indexed=False)
	status			= db.StringProperty()
	timestamp		= db.FloatProperty(indexed=False)
	created			= db.DateTimeProperty(auto_now_add=True)