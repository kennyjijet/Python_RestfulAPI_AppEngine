import webapp2

#controllers
#from controllers.Proxy 		import Proxy

# actions
from actions.testing		import testing
from actions.exam			import exam
from actions.noactions 		import noactions
from actions.saveplayer 	import saveplayer
from actions.setpntoken		import setpntoken
from actions.loadplayer 	import loadplayer
from actions.deleteplayer 	import deleteplayer
#from actions.savescore 		import savescore
#from actions.loadreplay 	import loadreplay
#from actions.getleaderboard import getleaderboard
from actions.deploy				import deploy
from actions.getdata            import getdata
from actions.getsoftstore		import getsoftstore
from actions.softpurchase		import softpurchase
from actions.hardpurchase		import hardpurchase
from actions.finishnow          import finishnow
from actions.getmyitems			import getmyitems
from actions.sendnotifications	import sendnotifications
from actions.event				import event

app = webapp2.WSGIApplication([
                                  ('/testing', testing),
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
                                  ('/deploy', deploy),
                                  ('/getdata', getdata),
                                  ('/getsoftstore', getsoftstore),
                                  ('/softpurchase', softpurchase),
                                  ('/hardpurchase', hardpurchase),
                                  ('/finishnow', finishnow),
                                  ('/getmyitems', getmyitems),
                                  ('/sendnotifications', sendnotifications),
                                  ('/event', event),
                                  ('/.*', noactions)
                              ], debug=True)
