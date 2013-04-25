from google.appengine.ext import db
	
class Item(db.Model):
	itemid 			= db.StringProperty()
	ownerid 		= db.StringProperty()
	status			= db.StringProperty()
	created			= db.DateTimeProperty(auto_now_add=True)