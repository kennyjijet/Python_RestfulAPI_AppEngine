import webapp2

#controllers
from controllers.Proxy 		import Proxy

# actions
#from actions.testing		import _populate, _cleanup
from actions.noactions 		import noactions
from actions.saveplayer 	import saveplayer
from actions.loadplayer 	import loadplayer
from actions.deleteplayer 	import deleteplayer
#from actions.savescore 		import savescore
#from actions.loadreplay 	import loadreplay
#from actions.getleaderboard import getleaderboard

from actions.deploystore 		import deploystore
from actions.getsoftstore		import getsoftstore
from actions.softpurchase		import softpurchase
from actions.verifyingstore		import verifyingstore

app = webapp2.WSGIApplication([
		#('/_populate', _populate),
		#('/_cleanup', _cleanup),
		#('/proxy', Proxy),
		('/saveplayer', saveplayer),
		('/loadplayer', loadplayer),
		('/deleteplayer', deleteplayer),
		#('/savescore', savescore),
		#('/loadreplay', loadreplay),
		#('/getleaderboard', getleaderboard),
		('/deploystore', deploystore),
		('/getsoftstore', getsoftstore),
		('/softpurchase', softpurchase),
		('/verifyingstore', verifyingstore),
		('/.*', noactions)
	], debug=True)
