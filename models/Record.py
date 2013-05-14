# built-in libraries
import hashlib

# google's libraries
from google.appengine.ext import db
from google.appengine.api import memcache

# config
from config			import config

class Record(db.Model):
	uuid 		= db.StringProperty()
	itid 		= db.StringProperty(indexed=False)
	hreceipt	= db.StringProperty()
	status		= db.StringProperty()
	updated		= db.DateTimeProperty(auto_now_add=True)
	
	@staticmethod
	def getrecord(self, uuid, itid, receipt):
		# hash receipt
		m = hashlib.md5()					# we need hashlib
		m.update(receipt)					# to hash our given receipt
		hreceipt = m.hexdigest()			# but our purpose is that we want to minimize the receipt and make it unique 
		# we will looking for our record in memcache first
		record = memcache.get(config.db['recorddb_name']+'.'+hreceipt)		# using hashed receipt as a key
		if record is None:					# if record was not found in memcahce
			records = Record.all().filter('hreceipt =', hreceipt).ancestor(db.Key.from_path('Record', config.db['recorddb_name'])).fetch(1) # then have a look in database (Datastore)
			if len(records)>=1: 			# count result, to see that how many record we've got, if more than one
				record = records[0]			# we only need one, so we pick the first one
			else:							# if record was not found, it means this record is new
				record = Record(parent=db.Key.from_path('Record', config.db['recorddb_name'])) #	# then we need to create a new record 
				record.uuid = uuid			# assign value
				record.itid = itid
				record.hreceipt = hreceipt
				record.status = 'pending'	# set default status as pending
				if record.put():			# put it into datastore
					memcache.delete(config.db['recorddb_name']+'.'+hreceipt)					# clean an existing record
					if not memcache.add(config.db['recorddb_name']+'.'+hreceipt, record, config.memcache['holdtime']):	# and re-add it into memcache, so if we need this data soon, we don't need to access datastore, which is expensive
						logging.warning('hardpurchase - Memcache set record failed')	# if failed, write into the log file
		if record is not None:
			if record.status == 'rewarded':	# if we can find the record from memcache or datastore, this record migth already been rewarded
				self.error = 'This item has been rewarded to user'	# if so, we shouldn't process any further, and inform user via error message
				record = None				# set record to none, so system won't process any further
		return record						# return
		
	
	@staticmethod
	def setrecord(self, record):
		if record:
			if record.put():
				memcache.delete(config.db['recorddb_name']+'.'+record.hreceipt)					# clean an existing record
				if not memcache.add(config.db['recorddb_name']+'.'+record.hreceipt, record, config.memcache['holdtime']):	# 
					logging.warning('hardpurchase - Memcache set record failed')				# if failed, write into the log file
				return True
		return False