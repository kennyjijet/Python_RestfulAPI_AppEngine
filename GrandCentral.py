import webapp2

#controllers
#from controllers.Proxy 		import Proxy

# actions
from actions.testing import testing
from actions.exam import exam
from actions.noactions import noactions
from actions.saveplayer import saveplayer
from actions.setpntoken import setpntoken
from actions.loadplayer import loadplayer
from actions.getplayerdata import getplayerdata
from actions.deleteplayer import deleteplayer
#from actions.savescore 		import savescore
#from actions.loadreplay 	import loadreplay
#from actions.getleaderboard import getleaderboard
from actions.deploy import deploy
from actions.getdata import getdata
from actions.getadvisor import getadvisor
from actions.getuilanglist import getuilanglist
from actions.getuitext import getuitext
from actions.getsoftstore import getsoftstore
from actions.softpurchase import softpurchase
from actions.hardpurchase import hardpurchase
from actions.finishnow import finishnow
from actions.getmyitems import getmyitems
from actions.getbuildingstore import getbuildingstore
from actions.buybuilding import buybuilding
from actions.upgradebuilding import upgradebuilding
from actions.finishbuilding import finishbuilding
from actions.getmybuildings import getmybuildings
from actions.collect import collect
from actions.getresearchlist import getresearchlist
from actions.startresearch import startresearch
from actions.getmyresearches import getmyresearches
from actions.finishresearch import finishresearch
from actions.sendnotifications import sendnotifications
from actions.event import event

app = webapp2.WSGIApplication([
								  #('/testing', testing),
								  #('/_cleanup', _cleanup),
								  #('/proxy', Proxy),
								  #('/exam', exam),
								  ('/saveplayer', saveplayer),
								  ('/setpntoken', setpntoken),
								  ('/loadplayer', loadplayer),
								  ('/getplayerdata', getplayerdata),
								  ('/deleteplayer', deleteplayer),
								  #('/savescore', savescore),
								  #('/loadreplay', loadreplay),
								  #('/getleaderboard', getleaderboard),
								  ('/deploy', deploy),
								  ('/getdata', getdata),
								  ('/getadvisor', getadvisor),
								  ('/getuilanglist', getuilanglist),
								  ('/getuitext', getuitext),
								  #('/getsoftstore', getsoftstore),
								  #('/softpurchase', softpurchase),
								  #('/hardpurchase', hardpurchase),
								  #('/finishnow', finishnow),
								  #('/getmyitems', getmyitems),
								  ('/getbuildingstore', getbuildingstore),
								  ('/buybuilding', buybuilding),
								  ('/upgradebuilding', upgradebuilding),
								  ('/finishbuilding', finishbuilding),
								  ('/getmybuildings', getmybuildings),
								  ('/collect', collect),
								  ('/getresearchlist', getresearchlist),
								  ('/startresearch', startresearch),
								  ('/getmyresearches', getmyresearches),
								  ('/finishresearch', finishresearch),
								  ('/sendnotifications', sendnotifications),
								  #('/event', event),
								  ('/.*', noactions)
							  ], debug=True)
