import webapp2

#controllers
from controllers.Proxy 		import Proxy

# actions
#from actions.testing		import _populate, _cleanup
from actions.exam			import exam
from actions.noactions 		import noactions
from actions.saveplayer 	import saveplayer
from actions.setpntoken		import setpntoken
from actions.loadplayer 	import loadplayer
from actions.deleteplayer 	import deleteplayer
#from actions.savescore 		import savescore
#from actions.loadreplay 	import loadreplay
#from actions.getleaderboard import getleaderboard

from actions.deploystore 		import deploystore
from actions.deployevent		import deployevent
from actions.getsoftstore		import getsoftstore
from actions.softpurchase		import softpurchase
from actions.hardpurchase		import hardpurchase
from actions.getmyitems			import getmyitems
from actions.sendnotifications	import sendnotifications

app = webapp2.WSGIApplication([
		#('/_populate', _populate),
		#('/_cleanup', _cleanup),
		#('/proxy', Proxy),
		('/exam', exam),
		('/saveplayer', saveplayer),
		('/setpntoken', setpntoken),
		('/loadplayer', loadplayer),
		('/deleteplayer', deleteplayer),
		#('/savescore', savescore),
		#('/loadreplay', loadreplay),
		#('/getleaderboard', getleaderboard),
		('/deploystore', deploystore),
		('/deployevent', deployevent),
		('/getsoftstore', getsoftstore),
		('/softpurchase', softpurchase),
		('/hardpurchase', hardpurchase),
		('/getmyitems', getmyitems),
		('/sendnotifications', sendnotifications),
		('/.*', noactions)
	], debug=True)
