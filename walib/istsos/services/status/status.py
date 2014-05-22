# -*- coding: utf-8 -*-
from walib.resource import waResourceService
from walib import databaseManager
from walib import utils

from datetime import datetime,timedelta
import time
from pytz import timezone

from lib import isodate as iso

import sys

class waStatus(waResourceService):
    
    def __init__(self,waEnviron):
        waResourceService.__init__(self,waEnviron)
        
    def executeGet(self):
        """
        Request:
            (...)/istsos/wa/istsos/<service name>/status/?type=delay
        
        The response is:
        >>> 
        [
            {
                "name": "air-rainfall",
                "children": [
                    {
                        "name": "ok",
                        "children": [
                            {}
                        ]
                    },
                    {
                        "name": "pending",
                        "children": [
                            {
                                "delay": 35243.204681,
                                "lastObservation": "2014-05-12T07:00:00+0200",
                                "code": [
                                    1,
                                    2,
                                    3
                                ],
                                "name": "LOCARNO",
                                "oum": "mm",
                                "exceptions": [
                                    {
                                        "status": "pending",
                                        "process": "acquisition",
                                        "datetime": "2014-05-12 09:00:00+02:00",
                                        "details": null,
                                        "message": "TypeError",
                                        "element": "LOCARNO",
                                        "id": 2
                                    }
                                ],
                                "lastMeasure": "2.000000",
                                "cycle": 4.894889539027778
                            },
                            {
                                "delay": 540143.269259,
                                "lastObservation": "2014-05-06T10:45:00+0200",
                                "code": [
                                    1,
                                    2,
                                    3
                                ],
                                "name": "P_LUGANO",
                                "oum": "mm",
                                "exceptions": [
                                    {
                                        "details": "No exception found"
                                    }
                                ],
                                "lastMeasure": "32.000000",
                                "cycle": 75.01989850819444
                            }
                        ]
                    },
                    {
                        "name": "verified",
                        "children": [
                            {
                                "delay": 49163.155455,
                                "lastObservation": "2014-05-12T03:08:00+0200",
                                "code": [
                                    1,
                                    2,
                                    3
                                ],
                                "name": "BELLINZONA",
                                "oum": "mm",
                                "exceptions": [
                                    {
                                        "status": "verified",
                                        "process": "acquisition",
                                        "datetime": "2014-05-12 05:00:00+02:00",
                                        "details": null,
                                        "message": "TypeError",
                                        "element": "BELLINZONA",
                                        "id": 1
                                    }
                                ],
                                "lastMeasure": "1.000000",
                                "type": "verified",
                                "cycle": 13.656432070833333
                            }
                        ]
                    }
                ]
            },
            {
                "name": "air-temperature",
                "children":[...]
                
            }
        ]            
        """    
        
        if self.service == "default":
            raise Exception("Status operation can not be done for default service instance.")
        
        servicedb = databaseManager.PgDB(
            self.serviceconf.connection['user'],
            self.serviceconf.connection['password'],
            self.serviceconf.connection['dbname'],
            self.serviceconf.connection['host'],
            self.serviceconf.connection['port'])
       
        param = self.waEnviron['parameters']['type'][0]
        
        procedureData = []  
        lastValue = { 'values' : 'No observation', 'uom' : 'No observation'}          
        for procedure in utils.getProcedureNamesList(servicedb,self.service):
            
            #position = utils.getGeoJSONFromProcedure(servicedb,self.service,procedure['name'],4326)
           
            if param == 'delay':
                status = self.__delay(procedure['name'],servicedb)
            else:
                raise Exception("Operation %s not permitted." % (param))                              

            if(status['status'] == 'NOT OK'):
                # Require last exceptions
                logEnviron = self.waEnviron.copy()                     
                logEnviron['parameters'] = {}
                from walib.istsos.services.logs import logs
                log = logs.waLogs(logEnviron)
                
                logEnviron['parameters'] = {'element': [procedure['name']], 'stime': [status['lastObservation']]}
                log.executeGet()

            if(status['lastObservation'] != 'No observation'):
                # Convert last Observation to string                
                status['lastObservation'] = status['lastObservation'].strftime("%Y-%m-%dT%H:%M:%S%z")
                lastValue = self.__getLastObservation(servicedb,procedure['name']) 
             
            procedureData.append(
                {
                    "procedure"   : procedure['name'],
                    "status"      : status,
                    "lastMeasure" : lastValue,
                    "exception"   : log.response['data']
                }                        
            )
        
        jsonResult = []
        for op in utils.getObsPropNamesList(servicedb,self.service):
            propOk = []
            propNotOk = []
            propVerif = []
            for procedure in procedureData:
                if self.__containsOp(servicedb,procedure,op['name']):
                    lastValue = self.__getLastValue(procedure,op['name'])
                    jsonProc = {
                                    "name"            : procedure['procedure'],
                                    "lastObservation" : procedure['status']['lastObservation'],
                                    "lastMeasure"     : lastValue['values'],
                                    "oum"             : lastValue['uom'], 
                                    "delay"           : procedure['status']['delay'],
                                    "cycle"           : procedure['status']['cycle']
                                }    
                    
                    if procedure['status']['status'] == "OK":
                        jsonProc['type'] = 'ok'
                        propOk.append(jsonProc)
                        
                    elif procedure['status']['status'] == "NOT OK":
                        code = [1,2,3]
                        
                        if procedure['exception']:
                            #for exc in procedure['exception']:
                            #    code.append(exc['code'])
                            jsonProc['code'] = code
                            jsonProc['exceptions'] = procedure['exception']
                            
                            if(procedure['exception'][0]['status'] == 'verified'):
                                jsonProc['type'] = 'verified'
                                propVerif.append(jsonProc)
                            else:
                                propNotOk.append(jsonProc)
                        else:
                            jsonProc['exceptions'] = [{"details" : "No exceptions found"}]
                            propNotOk.append(jsonProc)         
            
            if(len(propOk) == 0):
                propOk.append({})                        
            if(len(propNotOk) == 0):
                propNotOk.append({})
            if(len(propVerif) == 0):
                propVerif.append({})    

            jsonResult.append({
                "name" : op['name'],
                "children" : [
                    {"name" : "ok","children" : propOk },
                    {"name" :"pending", "children" : propNotOk},
                    {"name" : "verified", "children" : propVerif}
                ]              
                }
            )                
        
        self.setMessage("Status result")
        self.setData(jsonResult)


    def __getLastValue(self,procedureJson,opName):
        """
            retrun the last measurement        
        """
        for op in procedureJson['lastMeasure']:
            if op['op'] == opName:
                return op


    def __containsOp(self,servicedb, procedureJson,opName):      
        """
            check if the procedure contains the op
        """
        for op in procedureJson['lastMeasure']:
            if op['op'] == opName:
                return True
        return False
        
            
    def __delay(self,procedureName,servicedb):
        """
            Get the delay status (check last observation and sampling time) 
            return a dict containing status, last observation, delay (s), and cycle delay
        """
        
        sql ="""
        SELECT p.etime_prc as time, p.time_res_prc as delay
        FROM  %s.procedures p
        WHERE                    
        """ % (self.service,)
                    
        sql += """ p.name_prc = %s;                                       
        """
        par = (procedureName,)
        row = servicedb.select(sql, par)
        statusDict = {}     
        
        # if exist the procedure
        if len(row) == 1:            
            
            lastDate = row[0]['time']       
            delay = int(row[0]['delay'])            
                        
            nowDate = datetime.now().replace(tzinfo=timezone(time.tzname[0])) 
            
            limitDelay = timedelta(seconds=delay).total_seconds()
            tmpDelay = 0
            tmpCycle = 0

            if (lastDate == None):
                status = "No observation"
                lastDate = "No observation"
            else: 
                
                tmpDelta = (nowDate-lastDate).total_seconds()
                if(tmpDelta > limitDelay) and delay >0:
                    status = "NOT OK"
                    tmpDelay = tmpDelta          
                else:
                    status = "OK"
                    tmpDelay = limitDelay - tmpDelta
                
                #TODO: only for test?
                if limitDelay > 0:
                    tmpCycle = tmpDelta / limitDelay
                else:
                    tmpCycle = 0
                    tmpDelay = 0
 
            statusDict['status'] = status;
            statusDict['lastObservation'] = lastDate;
        else:    
            statusDict['status'] = "No observation";
            statusDict['lastObservation'] = "No observation";
                       
        statusDict['delay'] = tmpDelay  
        statusDict['cycle'] = tmpCycle            
        
        return statusDict                
            
            
    def __getLastObservation(self,servicedb,procedureName):
        """
            request the last observation
        """        
        opList = utils.getObservedPropertiesFromProcedure(servicedb,self.service,procedureName)
                
        name=""         
        
        for op in opList:
            name += op['name'] + ","
             
        offering = utils.getOfferingsFromProcedure(servicedb,self.service,procedureName)
        
        # request the last observation of the procedure
        rparams = {
            "request": "GetObservation",
            "service": "SOS",
            "version": "1.0.0",
            "procedure": procedureName,
            "observedProperty": name,
            "responseFormat": "application/json",
            "offering": offering[0]['name']
        }
        
        import lib.requests as requests
        
        response = requests.get(
            self.serviceconf.serviceurl["url"], 
            params=rparams
        )

        # Bad        
        dataArray = response.json['ObservationCollection']['member'][0]['result']['DataArray']
        
        # Value field
        data = []        
                    
        if not len(dataArray['values']) == 0:
            # last vaue field
            lastValue = dataArray['values'][0];
            # op and uom fileds
            field = dataArray['field']
            for i in range(1,len(lastValue)):
                data.append(
                    {
                        "values": lastValue[i],
                        "op" : field[i]['name'],
                        "uom" : field[i]['uom']                
                    }            
                )
            
        return data           