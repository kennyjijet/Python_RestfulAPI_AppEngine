from google.appengine.ext import db
	
class Score(db.Model):
	uuid 				= db.StringProperty()
	type 				= db.StringProperty()
	point				= db.FloatProperty()
	data 				= db.TextProperty()
	created_dwmy		= db.StringProperty()