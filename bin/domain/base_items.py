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

#==============================================================================

class DataSelectorException(Exception): pass

#==============================================================================

class LicenseServerException(Exception): pass

#==============================================================================

class BaseSolverType(object):
    
    container = SOLVER_TYPES
    NAME = ''
    
    #-------------------------------------------------------------------------
    @classmethod
    def getSolverTypeFromName(cls, name):
                
        for solverTypeName , solverType in SOLVER_TYPES.iteritems():
            if solverTypeName.lower() in name.lower():
                return solverType
        
        return None

#==============================================================================
@utils.registerClass
class AbaqusSolverType(BaseSolverType):
    
    NAME = 'ABAQUS'
    QUEUE_COLOUR = utils.ConsoleColors.BLUE

#==============================================================================
@utils.registerClass
class PamCrashSolverType(BaseSolverType):
    
    NAME = 'PamCrash'
    QUEUE_COLOUR = utils.ConsoleColors.GREEN
    
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
    TOKENS = [5, 6, 7, 8, 9, 10, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16,
        16, 17, 17, 18, 18, 18, 19, 19, 19, 20, 20, 20, 21, 21, 21, 21, 22, 
        22, 22, 22, 23, 23, 23]

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
    ID = 2
    CODE = 'abaqus3'
    QUEUE_CODE = 'qxt3'

#==============================================================================
@utils.registerClass
class Var2LicenseServerType(BaseLicenseServerType):
    
    NAME = 'VAR_2'
    ID = 1
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
    
#==============================================================================

class BaseExecutionServerType(object):
    
    container = EXECUTION_SERVER_TYPES
    NAME = ''
    NO_OF_CORES = 0
    NO_OF_GPU = 0
    DESCRIPTION = ''
    
    PATTERN = ''
    
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

class BaseDataSelector(object):
    
    DFT_OPTION_INDEX = 1
    DESCRIPTION = ''
    
    #-------------------------------------------------------------------------
    
    def __init__(self, parentApplication):
         
        self.parentApplication = parentApplication
    
    #-------------------------------------------------------------------------
    @staticmethod
    def printSelectionTitle(title):
        
        LENGTH = 80
        
        separator = '-'*((LENGTH - len(title) - 2)/2)
        additionalCharacter = (LENGTH - len(title) - 2) % 2
        
        print '%s %s %s' % (separator, title, separator + additionalCharacter*'-')
    
    #-------------------------------------------------------------------------
    
    def _getOptionFromList(self, description, prompt, options, multiSelection=False):
        
        # show message
        self.printSelectionTitle(description)
        
        optionNos = list()
        for iNo, option in enumerate(options):
            line = '{:>2}. {:}'.format(iNo + 1, option)
            # highlight default option
            if iNo + 1 == self.DFT_OPTION_INDEX:
                line = utils.ConsoleColors.OKGREEN + line + utils.ConsoleColors.ENDC
            
            print line
            optionNos.append(iNo + 1)
                        
        index = raw_input(prompt)
        
        if len(index) == 0:
            if multiSelection:
                return [self.DFT_OPTION_INDEX - 1, ]
            else:
                return self.DFT_OPTION_INDEX - 1
        
        try:
            # treat multi-selection option - must return a list
            if multiSelection:
                if index == 'a':
                    return [int(option) - 1 for option in optionNos]
                
                partsSpace = index.split(' ')
                partsComma = index.split(',')
                if partsSpace > 0 and len(partsSpace) > 1:
#                     print 'space sep', partsSpace
                    indexes = list()
                    for part in partsSpace:
                        # test for index error
                        option = options[int(part) - 1]
                        indexes.append(int(part) - 1)
                    return indexes
                elif partsComma > 0 and len(partsComma) > 1:
#                     print 'comma sep', partsComma
                    indexes = list()
                    for part in partsComma:
                        # test for index error
                        option = options[int(part) - 1]
                        indexes.append(int(part) - 1)
                    return indexes
                else:
#                     print 'other "%s"' % index
                    # prevent an 0. option
                    if int(index) == 0:
                        raise DataSelectorException()
                    
                    # test for index error
                    option = options[int(index) - 1]
                    return [int(index) - 1, ]
                
            # prevent an 0. option
            if int(index) == 0:
                index = None
            
            # test for index error
            option = options[int(index) - 1]
            
            return int(index) - 1
        except Exception as e:
            print '\tNot valid option: %s' % index
            print '\tPlease select one of numbers: %s' % optionNos
            
            return self._getOptionFromList(description, prompt, options, multiSelection)
    
    #-------------------------------------------------------------------------
    
    def getSelection(self):
        
        return
    
    #-------------------------------------------------------------------------
    
    def getOptions(self):
        
        return list()
    
    #--------------------------------------------------------------------------
    
    def indexToItem(self, index):
        
        return index
    
    #-------------------------------------------------------------------------
    @staticmethod
    def getTextInput(prompt, dftValue):
        
        text = raw_input(prompt)
        
        if len(text) == 0:
            return dftValue
        
        return text
    
    #-------------------------------------------------------------------------
    @classmethod
    def getTimeInput(cls, prompt, dftValue):
        
        text = raw_input(prompt)
        
        if len(text) == 0:
            return dftValue
        
        try:
            timeObject = time.strptime(text, '%m%d%H%M')
            timeString = time.strftime('%m%d%H%M', timeObject)
            
            return timeString
        
        except Exception as e:
            print '\tNot valid time format!'
            print '\tPlease provide time in a format: MMDDhhmm'
            
            return cls.getTimeInput(prompt, dftValue)        
        
    #-------------------------------------------------------------------------
    @classmethod
    def getIntInput(cls, description, prompt, minValue=0, maxValue=10, dftValue=5):
        
        # show message
        cls.printSelectionTitle(description)
                                
        value = raw_input(prompt)
        
        if len(value) == 0:
            return dftValue
        
        try:
            value = int(value)
            
            if value >= minValue and value <= maxValue:                                    
                return value
            else:
                raise DataSelectorException('Value out of range.')
            
        except Exception as e:
            print '\tNot valid value: %s' % value
            print '\tPlease select a number between %s and %s' % (minValue, maxValue)
            
            return cls.getIntInput(description, prompt, minValue, maxValue, dftValue)
        
        
#==============================================================================

class LicenseServerSelector(BaseDataSelector):
    
    DFT_OPTION_INDEX = 1
    DESCRIPTION = 'Available license servers'
    
    #-------------------------------------------------------------------------
    
    def getOptions(self):
        
        options = list()
        for licenseServer in LICENSE_SERVER_TYPES[:3]:   
            options.append(licenseServer.toOptionLine())
        
        return options
    
    #--------------------------------------------------------------------------
    
    def indexToItem(self, index):
#         
#         licenseServerList = self.getOptions()
        
        return LICENSE_SERVER_TYPES[:3][index]
    
    #-------------------------------------------------------------------------
    
    def getSelection(self):
        
        options = self.getOptions()
#         licenseServerList = self.getOptions()
#         
#         options = list()
#         for licenseServer in licenseServerList:
#             status = licenseServer.getTokenStatus()
#             options.append('%s %s license (free tokens: %s/%s)' % (
#                 licenseServer.LICENSE_TYPE.NAME, licenseServer.NAME, status['free'], status['total']))
                        
        # print list of servers
        index = self._getOptionFromList(
            self.DESCRIPTION,
            "Enter the number which represent ABAQUS queue [enter=%s]: " % self.DFT_OPTION_INDEX,
            options)
        
        return self.indexToItem(index)
    
#==============================================================================

class InputFileSelector(BaseDataSelector):
    
    FILE_EXT = ei.FileExtensions.ABAQUS_INPUT

#     def __init__(self, parentApplication):
#          
#         self.parentApplication = parentApplication
#         
#         # this is static to prevent content change in the middle of application run
#         self.filesList = glob.glob(os.path.join(
#             self.parentApplication.getWorkDir(), '*%s' % self.FILE_EXT))
            
    #--------------------------------------------------------------------------

    def getOptions(self):
        
        return glob.glob(os.path.join(self.parentApplication.getWorkDir(), '*%s' % self.FILE_EXT))
    
    #--------------------------------------------------------------------------
    
    def indexToItem(self, indexes):
        
        inpFiles = self.getOptions()
        
        return [inpFiles[index] for index in indexes]
    
    #--------------------------------------------------------------------------

    def getSelection(self):
        
        inpFiles = self.getOptions()
        
        # select input file
        if len(inpFiles) == 0:
            logging.error("Error: source *%s wasn't found!" % self.FILE_EXT)
            raise DataSelectorException("Error: source *%s wasn't found!" % self.FILE_EXT)
        elif len(inpFiles) == 1:
            return inpFiles
        else:
            indexes = self._getOptionFromList('Available input files',
                'Select input file(s) No. [1 or 1 2 ..., enter=%s, a=all]: ' % self.DFT_OPTION_INDEX,
                [os.path.basename(inpFileName) for inpFileName in inpFiles],
                multiSelection=True)
            
            return self.indexToItem(indexes)
            
#==============================================================================

class RestartInputFileSelector(InputFileSelector):
            
    def getSelection(self):
        
        inpFiles = self.getOptions()
        
        # select input file
        if len(inpFiles) == 0:
            raise DataSelectorException("Error: source *%s wasn't found!" % self.FILE_EXT)
        elif len(inpFiles) == 1:
            return inpFiles
        else:
            index = self._getOptionFromList('Available input files for restart',
                'Select input file No. [enter=%s]: ' % self.DFT_OPTION_INDEX,
                [os.path.basename(inpFileName) for inpFileName in inpFiles])
            
            return inpFiles[index]
    
#==============================================================================

class SolverVersionSelector(BaseDataSelector):
    
    DFT_OPTION_INDEX = 3
    DESCRIPTION = 'Choose the ABAQUS solver version'
    VERSIONS = ei.AbaqusSolverVersions
      
    #--------------------------------------------------------------------------
    
    def getOptions(self):

#TODO: load dynamically?
        
        versions = self.VERSIONS.SOLVER_LIST
        
        return versions
    
    #--------------------------------------------------------------------------

    def getSelection(self):
        
        options = self.getOptions()
        
        index = self._getOptionFromList(
            self.DESCRIPTION,
            'Enter number which represent version of solver[enter=%s]: ' % self.DFT_OPTION_INDEX,
            options)
            
        return options[index]
    
    #--------------------------------------------------------------------------
    
    def indexToItem(self, index):
         
        versions = self.getOptions()
#         return versions[index]
        
        return self.VERSIONS.getSolverPath(versions[index])
    
#==============================================================================

class ExecutionServerSelector(BaseDataSelector):
    
    DFT_OPTION_INDEX = 2
    DESCRIPTION = 'Choose the execution host'
    
    #--------------------------------------------------------------------------
    
    def getOptions(self):
        
#         hosts = self.parentApplication.profile.jobSettings.licenseServer.getAvailableHosts()
#         
#         # sort servers and user workstations
#         allHosts = list()
#         userHosts = list()
#         serverHosts = list()
#         for host in hosts:
#             if type(host) is WorkstationExecutionServerType:
#                 userHosts.append(host)
#             else:
#                 serverHosts.append(host)
        
        licenseServer = self.parentApplication.profile.jobSettings.licenseServer
        
        allHosts = list()
        userHosts = licenseServer.getWorkstations()
        serverHosts = licenseServer.getAPservers()
        
        allHosts.extend(serverHosts)
        allHosts.extend(userHosts)
        
        infoLines = list()
        for host in allHosts:
            infoLine = host.getInfoLine(licenseServer.CODE)
            infoLines.append(infoLine)
        
        # server type overview  
        description = 'Info - your computer is: %s' % self.parentApplication.profile.user.machine      
        for server in serverHosts:
            description += '\n\t%s (%s cores, %s GPU, %s, free cores: %s)' % (
                server.NAME, server.NO_OF_CORES, server.NO_OF_GPU, server.DESCRIPTION,
                server.freeCpuNo)
#             description += '\n\t' + server.getDescription()
                
        description += '\n\t%s' % WorkstationExecutionServerType.getDescription()
        
        return allHosts, infoLines, serverHosts, userHosts, description
    
    #--------------------------------------------------------------------------

    def getSelection(self):
        
        hosts, infoLines, serverHosts, userHosts, description = self.getOptions()
        
        description += '\nAvailable execution hosts for this queue'
        description += '\n' + 80*'-'
        description += '\nqueuename                      qtype resv/used/tot. load_avg    arch       states'
        description += '\n' + 80*'-'
        
        # highlight user machine   
        for optionIndex, host in enumerate(hosts):
            if host.isUserMachine:
                infoLine = infoLines[optionIndex]
                infoLines[optionIndex] = utils.ConsoleColors.OKBLUE + infoLine + utils.ConsoleColors.ENDC
        
        self.printSelectionTitle(self.DESCRIPTION)
        
        index = self._getOptionFromList(description, 
            "Enter the number which represent prefered execution host [enter=%s]: " % self.DFT_OPTION_INDEX,
            infoLines)
                        
        return hosts[index]
    
    #--------------------------------------------------------------------------
    
    def indexToItem(self, index):
        
        hosts, infoLines, serverHosts, userHosts, description = self.getOptions()
        
        return hosts[index]

#==============================================================================

class PamcrashInputFileSelector(InputFileSelector):
    
    FILE_EXT = ei.FileExtensions.PAMCRASH_INPUT
    
#==============================================================================

class PamCrashExecutionServerSelector(ExecutionServerSelector):
    
    DFT_OPTION_INDEX = 1

#==============================================================================

class PamCrashLicenseServerSelector(LicenseServerSelector):
    
    DFT_OPTION_INDEX = 1
    DESCRIPTION = 'Available license servers'
    
    #-------------------------------------------------------------------------
    
    def getOptions(self):
        
        return [LICENSE_SERVER_TYPES[3].toOptionLine()]
    
    #--------------------------------------------------------------------------
    
    def indexToItem(self, index):
        
        return LICENSE_SERVER_TYPES[3]

#==============================================================================

class PamCrashSolverVersionSelector(SolverVersionSelector):
    
    DFT_OPTION_INDEX = 1
    DESCRIPTION = 'Choose the PamCrash solver version'
    VERSIONS = ei.PamcrashSolverVersions            

    
