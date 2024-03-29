import webapp2

#controllers
#from controllers.Proxy 		import Proxy

# actions
from actions.saveplayer import saveplayer
from actions.setpntoken import setpntoken
from actions.getplayerdata import getplayerdata
from actions.getplayerbasicdatas import getplayerbasicdatas
from actions.deleteplayer import deleteplayer
from actions.advicechecklist import advicechecklist

from actions.deploy import deploy
from actions.deploy_pro7 import deploy_pro7
from actions.getdata import getdata
from actions.getadvisor import getadvisor
from actions.getuilanglist import getuilanglist
from actions.getuitext import getuitext
from actions.getbuildingstore import getbuildingstore
from actions.buybuilding import buybuilding
from actions.upgradebuilding import upgradebuilding
from actions.finishbuilding import finishbuilding
from actions.finishrace import finishrace
from actions.getmybuildings import getmybuildings
from actions.collect import collect

from actions.carbuy import carbuy
from actions.carlist import carlist
from actions.carupgrade import carupgrade

from actions.challengecreate import challengecreate
from actions.challengelist import challengelist
from actions.challengeupdate import challengeupdate
from actions.challengeview import challengeview
from actions.challengedelete import challengedelete
from actions.getrecentplayerlist import getrecentplayerlist

from actions.getresearchlist import getresearchlist
from actions.startresearch import startresearch
from actions.getmyresearches import getmyresearches
from actions.finishresearch import finishresearch
from actions.sendnotifications import sendnotifications
from actions.clean import clean

from actions.ping import ping
from actions.force500 import force500

from test.get_data_item import get_data_item
from test.test_score import test_score

app = webapp2.WSGIApplication([
                                  ('/saveplayer', saveplayer),
                                  ('/setpntoken', setpntoken),
                                  ('/getplayerdata', getplayerdata),
                                  ('/getplayerbasicdatas', getplayerbasicdatas),
                                  ('/deleteplayer', deleteplayer),
                                  ('/advicechecklist', advicechecklist),
                                  ('/deploy', deploy),
                                  ('/deploy_pro7', deploy_pro7),
                                  ('/getdata', getdata),
                                  ('/getadvisor', getadvisor),
                                  ('/getuilanglist', getuilanglist),
                                  ('/getuitext', getuitext),
                                  ('/getbuildingstore', getbuildingstore),
                                  ('/buybuilding', buybuilding),
                                  ('/upgradebuilding', upgradebuilding),
                                  ('/finishbuilding', finishbuilding),
                                  ('/finishrace', finishrace),

                                  ('/getmybuildings', getmybuildings),
                                  ('/collect', collect),

                                  ('/carbuy', carbuy),
                                  ('/carlist', carlist),
                                  ('/carupgrade', carupgrade),

                                  ('/challengecreate', challengecreate),
                                  ('/challengelist', challengelist),
                                  ('/challengeupdate', challengeupdate),
                                  ('/challengeview', challengeview),
                                  ('/challengedelete', challengedelete),
                                  ('/getrecentplayerlist', getrecentplayerlist),

                                  ('/getresearchlist', getresearchlist),
                                  ('/startresearch', startresearch),
                                  ('/getmyresearches', getmyresearches),
                                  ('/finishresearch', finishresearch),

                                  ('/sendnotifications', sendnotifications),
                                  ('/ping', ping),
                                  ('/force500', force500),
                                  ('/getdataitem', get_data_item),
                                  ('/test/score', test_score),
                                  ('/clean', clean)
                              ], debug=True)
