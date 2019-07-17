#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Python script for '''

import os
import sys
import glob
import shutil
import time
import re
import logging
from string import Template

import utils
import enum_items as ei
# from interfaces import xmlio

#==============================================================================

LICENSE_TYPES = dict()
LICENSE_SERVER_TYPES = list()
EXECUTION_SERVER_TYPES = dict()
PAMCRASH_LICENSE_SERVER_TYPES = list()
NASTRAN_LICENSE_SERVER_TYPES = list()
SOLVER_TYPES = dict()
POST_PROCESSING_TYPES = list()

#==============================================================================

class LicenseServerException(Exception): pass

#==============================================================================

class BaseSolverType(object):
    
    container = SOLVER_TYPES
    NAME = ''
    POST_PROCESSING_TYPES = list()
    
    #-------------------------------------------------------------------------
    @classmethod
    def getSolverTypeFromName(cls, name):
                
        for solverTypeName , solverType in SOLVER_TYPES.iteritems():
            if solverTypeName.lower() in name.lower():
                return solverType
        
        return UnknownSolverType
    
    #-------------------------------------------------------------------------
    @classmethod
    def registerPostProcessingType(cls, postType):
        
        if postType.NAME not in [p.NAME for p in cls.POST_PROCESSING_TYPES]:
            cls.POST_PROCESSING_TYPES.append(postType)
        

#==============================================================================
@utils.registerClass
class UnknownSolverType(BaseSolverType):
    
    NAME = 'UNKNOWN'
    QUEUE_COLOUR = utils.ConsoleColors.FAIL
    JOB_ITEM_COLOUR = utils.TreeItemColors.RED
    
#==============================================================================
@utils.registerClass
class AbaqusSolverType(BaseSolverType):
    
    NAME = 'ABAQUS'
    QUEUE_COLOUR = utils.ConsoleColors.BLUE
    JOB_ITEM_COLOUR = utils.TreeItemColors.BLUE
    POST_PROCESSING_TYPES = list()

#==============================================================================
@utils.registerClass
class PamCrashSolverType(BaseSolverType):
    
    NAME = 'PamCrash'
    QUEUE_COLOUR = utils.ConsoleColors.GREEN
    JOB_ITEM_COLOUR = utils.TreeItemColors.GREEN
    POST_PROCESSING_TYPES = list()
    
#==============================================================================
@utils.registerClass
class NastranSolverType(BaseSolverType):
    
    NAME = 'NASTRAN'
    QUEUE_COLOUR = utils.ConsoleColors.CYAN
    JOB_ITEM_COLOUR = utils.TreeItemColors.CYAN
    POST_PROCESSING_TYPES = list()

#==============================================================================
@utils.registerClass
class ToscaSolverType(BaseSolverType):
    
    NAME = 'TOSCA'
    QUEUE_COLOUR = utils.ConsoleColors.MAGENTA
    JOB_ITEM_COLOUR = utils.TreeItemColors.MAGENTA
    POST_PROCESSING_TYPES = list()
    
#==============================================================================

class BaseLicenseType(object):
    
    container = LICENSE_TYPES
    TOKENS = []
    
    #-------------------------------------------------------------------------
    
    @classmethod
    def getNoOfTokens(cls, cpuNo):
        
        return cls.TOKENS[cpuNo - 1]
    
    #-------------------------------------------------------------------------
    
    @classmethod
    def getNoOfCpus(cls, tokenNo):
        
        # not enough tokens for submit
        if tokenNo < cls.TOKENS[0]:
            return 0
        
        if tokenNo not in cls.TOKENS:
            return cls.getNoOfCpus(tokenNo - 1)
        else:
            return cls.TOKENS.index(tokenNo) + 1

#==============================================================================
@utils.registerClass
class FlexLicenseType(BaseLicenseType):
    
    NAME = 'flex'
    TOKENS = [
        5, 6, 7, 8, 9, 10, 11, 12, 12, 13,
        13, 14, 14, 15, 15, 16, 16, 16, 17, 17,
        18, 18, 18, 19, 19, 19, 20, 20, 20, 21,
        21, 21, 21, 22, 22, 22, 22, 23, 23, 23]

#==============================================================================
@utils.registerClass
class DslsLicenseType(BaseLicenseType):
    
    NAME = 'dsls'
    TOKENS = [50, 59, 68, 76, 85, 94, 103, 111, 120, 125,
            130, 135, 140, 144, 149, 153, 157, 160, 165, 168,
            172, 175, 179, 182, 185, 188, 192, 195, 198, 200,
            203, 206, 209, 212, 214, 217, 220, 222, 225, 227]

#==============================================================================
@utils.registerClass
class PamcrashLicenseType(BaseLicenseType):
    
    NAME = 'PamCrash'
    TOKENS = [26, 26, 27, 29, 29, 30, 31, 32, 32, 32,
              33, 33, 34, 34, 34, 35, 35, 35, 35, 35,
              36, 36, 36, 36, 36, 37, 37, 37, 37, 37,
              37, 38]

#==============================================================================
@utils.registerClass
class NastranLicenseType(BaseLicenseType):
    
    NAME = 'Nastran'
    TOKENS = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
              1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
              1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
              1, 1]
        
#==============================================================================

class BaseLicenseServerType(object):
    
    container = LICENSE_SERVER_TYPES
    
    LICENSE_TYPE = DslsLicenseType
    
    resources = None
    
    #-------------------------------------------------------------------------
    @classmethod
    def toOptionLine(cls):
        
        status = cls.getTokenStatus()
        optionLine = '%s %s license (free tokens: %s/%s)' % (
            cls.LICENSE_TYPE.NAME, cls.NAME, status['free'], status['total'])
        
        return optionLine
    
    #-------------------------------------------------------------------------
    @classmethod
    def connectResources(cls, resources):
        cls.resources = resources 
    
    #-------------------------------------------------------------------------
    @classmethod
    def getNoOfTokens(cls, cpuNo):
        return cls.LICENSE_TYPE.getNoOfTokens(cpuNo)
    
    #-------------------------------------------------------------------------
    @classmethod
    def getNoOfCpus(cls, tokenNo):
        return cls.LICENSE_TYPE.getNoOfCpus(tokenNo)
        
    #--------------------------------------------------------------------------
    @classmethod
    def getAvailableHosts(cls):
        
        return cls.resources.availableLicenseServerHosts[cls]
        
#         stdout, _ = utils.runSubprocess('qstat -f -q %s' % cls.CODE)
#         
#         lines = stdout.splitlines()
#         
#         hosts = list()
#         for line in lines:
#             line = line.strip()
#             if not line.startswith(cls.CODE):
#                 continue
#             
#             parts = line.split()
#             nameString = parts[0]
#             executionServer = BaseExecutionServerType.getServerFromName(nameString)
#             executionServer.setInfoLine(line)
#             hosts.append(executionServer)
#             
#         return hosts
    
    #--------------------------------------------------------------------------
    @classmethod
    def getUserMachine(cls):
        
        for host in cls.getAvailableHosts():
            if host.isUserMachine:
                return host
        
        return None
    
    #--------------------------------------------------------------------------
    @classmethod
    def getAPservers(cls):
        
        aps = list()
        for host in cls.getAvailableHosts():
            if type(host) is not WorkstationExecutionServerType:
                aps.append(host)
        return aps
    
    #--------------------------------------------------------------------------
    @classmethod
    def getWorkstations(cls):
        
        ws = list()
        for host in cls.getAvailableHosts():
            if type(host) is WorkstationExecutionServerType:
                ws.append(host)
        return ws
    
    #--------------------------------------------------------------------------
    @classmethod
    def getTokenStatus(cls):
        
        return cls.resources.tokenStatus[cls]
#         
#         stdout, _ = utils.runSubprocess(cls.QLIC_COMMAND)
#         
#         lines = stdout.splitlines()
#         # locate corresponding line
#         for line in lines:
#             if cls.QUEUE_CODE in line:
#                 break
#             
#         status = dict()
#         for label, value in zip(cls.QLIC_COUMNS,line.split()):
#             if label != 'resource':
#                 try:
#                     value = int(value)
#                 except ValueError as e:
#                     value = 0
#             status[label] = value
#         
#         return status
    
    #--------------------------------------------------------------------------
    @classmethod
    def getLicenseServerTypeFromName(cls, licenseServerQueueCode):
        
        ''' licenseServerQueueCode = abaqus1@* '''
        
        for licenseServer in LICENSE_SERVER_TYPES:
            if licenseServer.CODE in licenseServerQueueCode:
                return licenseServer
        
        raise LicenseServerException(
            'Unknown license server pattern: %s' % licenseServerQueueCode)
        
    #--------------------------------------------------------------------------
#     @classmethod
#     def getUserTokenStatus(cls, userName, hostName):
#         
#         ''' Identifies type and number of tokens used by given user jobs.'''
#         
#         licenseServerQueueCodes = dict()
#         for licenseServer in LICENSE_SERVER_TYPES:
#             licenseServerQueueCodes[licenseServer.QUEUE_CODE] = licenseServer
#                 
#         stdout, _ = utils.runSubprocess(cls.QLIC_COMMAND + ' -w')
#         lines = stdout.splitlines()
#         
#         for line in lines:
#             parts = line.split()
#             if len(parts) == 2 and parts[0]:
#                 licenseServerQueueCode = parts[0].strip()
#             
#             # skip different queues
#             if licenseServerQueueCode not in licenseServerQueueCodes:
#                 continue
#             
#             if userName in line and hostName in line:
#                 # running job                    
#                 if '@' in line:
#                     # identify license server
#                     licenseServer = licenseServerQueueCodes[licenseServerQueueCode]
#                     noOfTokens = int(parts[-1].split('=')[-1])
#                     return licenseServer, noOfTokens 
#                 
#         return None, 0
    
    #--------------------------------------------------------------------------
    @classmethod
    def getFreeFromTokens(cls, tokensRequired):
        
        for licenseServer in LICENSE_SERVER_TYPES:
            status = licenseServer.getTokenStatus()
            if int(status['free']) > tokensRequired:
                return licenseServer
            
        return None
    
    #--------------------------------------------------------------------------
    @classmethod
    def getFree(cls, code):
        
        freeTokens = 0
        freeLicenseServer = None
        for licenseServer in LICENSE_SERVER_TYPES:            
            if code.lower() not in licenseServer.CODE.lower():
                continue
            status = licenseServer.getTokenStatus()
            if int(status['free']) > freeTokens:
                freeTokens = int(status['free'])
                freeLicenseServer = licenseServer
            
        return freeLicenseServer
    
    
        

#==============================================================================
@utils.registerClass
class Var1LicenseServerType(BaseLicenseServerType):
    
    NAME = 'VAR_1'
    ID = 1
    CODE = 'abaqus3'
    QUEUE_CODE = 'qxt3'

#==============================================================================
@utils.registerClass
class Var2LicenseServerType(BaseLicenseServerType):
    
    NAME = 'VAR_2'
    ID = 2
    CODE = 'abaqus2'
    QUEUE_CODE = 'qxt2'

#==============================================================================
@utils.registerClass
class CommercialLicenseServerType(BaseLicenseServerType):
    
    NAME = 'COMMERCIAL'
    ID = 0
    CODE = 'abaqus1'
    QUEUE_CODE = 'qxt1'

#==============================================================================
@utils.registerClass
class PamCrashLicenseServerType(BaseLicenseServerType):
    
#     container = PAMCRASH_LICENSE_SERVER_TYPES
    
    NAME = 'PAMCRASH'
    ID = 3
    CODE = 'pamcrash1'
    QUEUE_CODE = 'pamcrash1'
    
    LICENSE_TYPE = PamcrashLicenseType

#==============================================================================
@utils.registerClass
class NastranLicenseServerType(BaseLicenseServerType):
    
#     container = NASTRAN_LICENSE_SERVER_TYPES
    
    NAME = 'NASTRAN'
    ID = 4
    CODE = 'nastran'
    QUEUE_CODE = 'nastran'
    
    LICENSE_TYPE = NastranLicenseType
    
#==============================================================================

class BaseExecutionServerType(object):
    
    container = EXECUTION_SERVER_TYPES
    NAME = ''
    NO_OF_CORES = 0
    NO_OF_GPU = 0
    DESCRIPTION = ''
    
    PATTERN = ''
    
    SOLVER_PARAMS = None
    
    resources = None
    
    #-------------------------------------------------------------------------
    
    def __init__(self, name, fullName):
        
        self.name = name
        self.fullName = fullName
        
        self.infoLine = ''
        
        self.runningJobs = dict()
#         self.freeCpuNo = self.NO_OF_CORES
        self.isUserMachine = False
        
        self._identityUserMaschine()
        self._checkRunningJobs()
                
    #-------------------------------------------------------------------------
    
    def _checkRunningJobs(self):
        
        usedCpuNo = 0
        for jobId, attrs in self.getRuningJobs().iteritems():
            if attrs['job_state'] == 'r':
                job = self.resources.jobsInQueue[jobId]
#                 noOfTokens = int(job['hard_request'])
#                 
#                 licenceServer = BaseLicenseServerType.getLicenseServerTypeFromName(
#                     job['hard_req_queue'])
#             
# #                 licenceServer, noOfTokens = BaseLicenseServerType.getUserTokenStatus(
# #                     attrs['job_owner'], self.name)
# #                 
# #                 # in case of job running for a different solver
# #                 if licenceServer is None:
# #                     continue
#                 
#                 noOfCpus = licenceServer.getNoOfCpus(noOfTokens)
#                 attrs['used_cpus'] = noOfCpus
#                 attrs['licenceServer'] = licenceServer
#                 attrs['used_tokens'] = noOfTokens
                usedCpuNo += job.noOfCpus
                
                self.runningJobs[jobId] = job
        
        self.freeCpuNo = self.NO_OF_CORES - usedCpuNo
            
    #-------------------------------------------------------------------------
    
    def _identityUserMaschine(self):
        
        userName, machine, email = utils.getUserInfo()
        if machine in self.fullName:
            self.isUserMachine = True
        
    #-------------------------------------------------------------------------
    
    def getResources(self):
        
        return self.resources.getHostStat(self.fullName.split('@')[1])
    
    #-------------------------------------------------------------------------
    
    def getRuningJobs(self):
        
        resources = self.resources.getHostStat(self.fullName.split('@')[1])
        return resources['jobs']
    
    #-------------------------------------------------------------------------
    
    def setInfoLine(self, infoLine):
        
        self.infoLine = infoLine
    
    #-------------------------------------------------------------------------
    
    def getInfoLine(self, prefix=''):
                 
        # add running jobs info
#         for jobId, attrs in self.getRuningJobs().iteritems():
#             licenceServer, noOfTokens = BaseLicenseServerType.getUserTokenStatus(
#                 attrs['job_owner'], self.name)
#             if attrs['job_state'] == 'r':        
#                 self.infoLine += '\n\tRunning job: %s (%s uses %s %s tokens)' % (
#                     jobId, attrs['job_owner'], noOfTokens, licenceServer.NAME)#, attrs['job_name'])
#             else:
#                 self.infoLine += '\n\tJob: %s - status: %s (%s uses %s %s tokens)' % (
#                     jobId, attrs['job_state'], attrs['job_owner'], noOfTokens, licenceServer.NAME)#, attrs['job_name'])
        
        
        resources = self.getResources()
        
        pattern = '{}{:>%s}' % str(55 - len(prefix + self.fullName))
        self.infoLine = pattern.format(prefix + self.fullName, resources['load_avg']) 
        
        for job in self.runningJobs.values():
            self.infoLine += '\n\tRunning job: %s (%s uses %s %s tokens %s CPUs)' % (
                job.id, job['JB_owner'], job.noOfTokens, job.licenceServer.NAME, job.noOfCpus)
        
#         # highlight user machine        
#         if self.isUserMachine:
#             self.infoLine = utils.ConsoleColors.OKBLUE + self.infoLine + utils.ConsoleColors.ENDC
# #                        
        return self.infoLine
    
#     #-------------------------------------------------------------------------
#     @classmethod
#     def connectLicenseServerTypes(cls, licenseServerTypes):
#         
#         cls.licenseServerTypes = licenseServerTypes
        
    #-------------------------------------------------------------------------
#     @classmethod
#     def connectResources2(cls):
#         cls.resources = Resources()
        
    #-------------------------------------------------------------------------
    @classmethod
    def connectResources(cls, resources):
        cls.resources = resources
    
    #-------------------------------------------------------------------------
    @classmethod
    def getDescription(cls):
         
        return '%s (%s cores, %s GPU, %s, free cores:N/A)' % (
            cls.NAME, cls.NO_OF_CORES, cls.NO_OF_GPU, cls.DESCRIPTION)
    
#     def getDescription(self):
#         return '%s (%s cores, %s GPU, %s, free cores: %s)' % (
#                 self.NAME, self.NO_OF_CORES, self.NO_OF_GPU, self.DESCRIPTION,
#                 self.freeCpuNo)
    
    #-------------------------------------------------------------------------
    @classmethod
    def getServerFromName(cls, nameString):
        
        for serverType in EXECUTION_SERVER_TYPES.values():
            matchServer = re.match(serverType.PATTERN, nameString)
            if matchServer:
                return serverType(matchServer.group(1), nameString)
                
        raise DataSelectorException('Server name not recognised! name=%s' % nameString)
    
    #-------------------------------------------------------------------------
    @classmethod
    def getDftCoreNumber(cls):
        return cls.NO_OF_CORES
    
    #-------------------------------------------------------------------------
    @classmethod
    def getLoad(cls):
        return

#==============================================================================
@utils.registerClass
class So1ExecutionServerType(BaseExecutionServerType):
    
    NAME = 'server mb-so1'
    NO_OF_CORES = 12
    NO_OF_GPU = 1
    DESCRIPTION = 'low performance'
    
    PATTERN = r'.*@(.*-so1)\.cax\.lan'
       
    
#==============================================================================
@utils.registerClass
class So2ExecutionServerType(BaseExecutionServerType):
    
    NAME = 'server mb-so2'
    NO_OF_CORES = 12
    NO_OF_GPU = 1
    DESCRIPTION = 'middle performance'
    
    PATTERN = r'.*@(.*-so2)\.cax\.lan'

#==============================================================================
@utils.registerClass
class So3ExecutionServerType(BaseExecutionServerType):
    
    NAME = 'server mb-so3'
    NO_OF_CORES = 32
    NO_OF_GPU = 2
    DESCRIPTION = 'best performance'
    
    PATTERN = r'.*@(.*-so3)\.cax\.lan'
    
    SOLVER_PARAMS = 'threads=4'

#==============================================================================
@utils.registerClass
class So4ExecutionServerType(BaseExecutionServerType):
     
    NAME = 'server mb-so4'
    NO_OF_CORES = 32
    NO_OF_GPU = 0
    DESCRIPTION = 'best performance'
     
    PATTERN = r'.*@(.*-so4)\.cax\.lan'
    
#==============================================================================
@utils.registerClass
class WorkstationExecutionServerType(BaseExecutionServerType):
    
    NAME = 'user workstation'
    NO_OF_CORES = 4
    NO_OF_GPU = 0
    DESCRIPTION = 'not recommended'
    
    PATTERN = r'.*@(.*-u.*)\.cax\.lan'
    
    #-------------------------------------------------------------------------
    @classmethod
    def getDftCoreNumber(cls):
        return cls.NO_OF_CORES - 1

#==============================================================================

class BasePostProcessingType(object):
    
    container = POST_PROCESSING_TYPES
    NAME = ''
    
    def __init__(self, parentJob):
        
        self.parentJob = parentJob
    
    #--------------------------------------------------------------------------
    
    def getContent(self):
        
        return ''

#==============================================================================
@utils.registerClass
class NoPostProcessingType(BasePostProcessingType):
    
    NAME = 'No postprocessing'
    ID = 0
    
#==============================================================================
@utils.registerClass
class MetaConversionPostProcessingType(BasePostProcessingType):
    
    NAME = 'Use local Meta_queue_session.ses'
    ID = 1
    
    #--------------------------------------------------------------------------
    
    def getContent(self):
        
        template = Template('''
# postprocessing - conversion to metadb
if [ -r META_queue_session.ses -a -f $meta_executable ]; then
    echo "Starting conversion to Metadb"
    echo "Starting conversion to Metadb" >> $jobname.log
    $meta_executable -b -foregr -virtualx_64bit -s META_queue_session.ses $jobname &>> $jobname.log
    sleep 5
    echo "Conversion to Metadb finished"
    echo "Conversion to Metadb finished" >> $jobname.log
fi
''')

        return template.safe_substitute(
            {'jobname' : self.parentJob.inpFile.baseName,
             'meta_executable' : ei.META_EXECUTABLE})

# #==============================================================================
# @utils.registerClass
# class ResultsDeletingPostProcessingType(BasePostProcessingType):
#     
#     NAME = 'Results deleting'
#     ID = 2

#==============================================================================

class BaseMetaPostProcessingType(BasePostProcessingType):
    
#     NAME = ''
#     ID = 1
    metaSessionPath = ''
                
    #--------------------------------------------------------------------------
    
    def getContent(self):
        
        template = Template('''
# postprocessing - META
metaSessionName=$meta_session_name
if [ -r $metaSessionName -a -f $meta_executable ]; then
    echo "Starting META postprocessing"
    echo "Starting META postprocessing" >> $jobname.log
    $meta_executable -b -foregr -virtualx_64bit -s $metaSessionName $jobname &>> $jobname.log
    sleep 5
    echo "META postprocessing finished"
    echo "META postprocessing finished" >> $jobname.log
fi
''')

        return template.safe_substitute(
            {'jobname' : self.parentJob.inpFile.baseName,
             'meta_executable' : ei.META_EXECUTABLE,
             'meta_session_name' : self.metaSessionPath})

