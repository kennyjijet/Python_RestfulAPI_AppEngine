from google.appengine.ext import db

class Record(db.Model):
	uuid 		= db.StringProperty()
	itemid 		= db.StringProperty(indexed=False)
	hreceipt	= db.StringProperty()
	status		= db.StringProperty()
	updated		= db.DateTimeProperty(auto_now_add=True)