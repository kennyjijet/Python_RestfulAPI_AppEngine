import time
import json
import uuid
import logging

# config
from config import config
# built-in libraries
from random import randint
from datetime import datetime
from GCVars import GCVars

from google.appengine.api import namespace_manager

class Utils(object):

    @staticmethod
    def reset(self):
        self.sinfo = ''
        self.respn = ''
        self.error = ''
        self.debug = ''
        self.game = self.request.get(GCVars.game) or ''
        namespace_manager.set_namespace(self.game)
        logging.debug('Using namespace ' + self.game)


    @staticmethod
    def required(self, par_name):
        if self.error == "":
            if self.request.get(par_name):
                return self.request.get(par_name)
            else:
                self.error = par_name + " is a required parameter. IP Logged."
                logging.warn(self.error)
        return "undefined"

    @staticmethod
    def geneuuid(self, par_name):
        if self.request.get(par_name):
            return self.request.get(par_name)
        else:
            return 'uuid-'+str(uuid.uuid4()) #now.strftime('%m%H%d')+str(randint(1, 1000000))

    @staticmethod
    def genitemid(self):
        return 'item-'+str(uuid.uuid4()) #now.strftime('item%m%H%d')+str(randint(1, 1000000))

    @staticmethod
    def genanyid(self, any):
        return any+'-'+str(uuid.uuid4()) #now.strftime(str(any)+'%m%H%d')+str(randint(1, 1000000))

    @staticmethod
    def GetRandomOfNumberInArray(self, size, _range):
        arr = []
        for i in range(0, size):
            while True:
                number = randint(0, _range-1)
                try:
                    arr.index(number)
                except ValueError:
                    arr.append(number)
                    break
        return arr

    @staticmethod
    def RESTreturn(self, time_taken, debug=True):
        stampNow = int(time.time())
        self.debug += '('+str(time_taken)+')'
        if self.error != "":
            logging.warn(self.error)
        if self.respn == '':
            self.respn = '""'
        else:
            if (self.respn[0] != '{' or self.respn[len(self.respn)-1] != '}') and (self.respn[0] != '[' or self.respn[len(self.respn)-1] != ']') and (self.respn[0] != '"' or self.respn[len(self.respn)-1] != '"'):
                self.respn = '"'+self.respn+'"'
        self.sinfo = '{"serverName":"'+config.server['serverName']+'","apiVersion":'+str(config.server['apiVersion'])+',"action":"'+type(self).__name__+'","requestDuration":'+str(time_taken)+',"currentTime":'+str(stampNow)+'}'
        response = ""
        if self.request.get('debug'):
            response = '{"serverInformation":'+self.sinfo+',"response":'+self.respn+',"game":"'+namespace_manager.get_namespace()+'","error":"'+self.error+'", "debug":"'+self.debug+'"}'
        else:
            response = '{"serverInformation":'+self.sinfo+',"response":'+self.respn+',"game":"'+namespace_manager.get_namespace()+'","error":"'+self.error+'"}'



        if debug:
            Utils.LogResponse(self,response)

        if ( self.error is not None and self.error != '' ) :
            logging.warn(self.error)
        return response

    @staticmethod
    def LogRequest(self):
        txt = type(self).__name__+'?'
        for field in self.request.arguments():
            txt += field+'='+self.request.get(field)+'&'
        txt = txt.rstrip('&')
        logging.debug(txt)

    @staticmethod
    def LogResponse(self, response):
        txt = '"'+type(self).__name__+'":'
        logging.debug(txt+response)