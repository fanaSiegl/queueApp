#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Python script for '''

import os
import sys
import glob
import shutil
import numpy as np
import time
import re

import utils
import enum_items as ei
from interfaces import xmlio

#==============================================================================

LICENSE_TYPES = dict()
LICENSE_SERVER_TYPES = list()
EXECUTION_SERVER_TYPES = dict()
PAMCRASH_LICENSE_SERVER_TYPES = list()
NASTRAN_LICENSE_SERVER_TYPES = list()

#==============================================================================

class DataSelectorException(Exception): pass

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
    QLIC_COMMAND = 'qlic'
    QLIC_COUMNS = ['resource', 'total', 'limit', 'extern', 'intern', 'wait', 'free']
    
    LICENSE_TYPE = DslsLicenseType

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
                
        stdout, _ = utils.runSubprocess('qstat -f -q %s' % cls.CODE)
        
        lines = stdout.splitlines()
        
        hosts = list()
        for line in lines:
            line = line.strip()
            if not line.startswith(cls.CODE):
                continue
            
            parts = line.split()
            nameString = parts[0]
            executionServer = BaseExecutionServerType.getServerFromName(nameString)
            executionServer.setInfoLine(line)
            hosts.append(executionServer)
            
        return hosts
    
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
        
        stdout, _ = utils.runSubprocess(cls.QLIC_COMMAND)
        
        lines = stdout.splitlines()
        # locate corresponding line
        for line in lines:
            if cls.QUEUE_CODE in line:
                break
            
        status = dict()
        for label, value in zip(cls.QLIC_COUMNS,line.split()):
            if label != 'resource':
                try:
                    value = int(value)
                except ValueError as e:
                    value = 0
            status[label] = value
        
        return status
    
    #--------------------------------------------------------------------------
    @classmethod
    def getUserTokenStatus(cls, userName, hostName):
        
        ''' Identifies type and number of tokens used by given user jobs.'''
        
        licenseServerQueueCodes = dict()
        for licenseServer in LICENSE_SERVER_TYPES:
            licenseServerQueueCodes[licenseServer.QUEUE_CODE] = licenseServer
                
        stdout, _ = utils.runSubprocess(cls.QLIC_COMMAND + ' -w')
        lines = stdout.splitlines()
        
        for line in lines:
            parts = line.split()
            if len(parts) == 2 and parts[0]:
                licenseServerQueueCode = parts[0].strip()
            
            # skip different queues
            if licenseServerQueueCode not in licenseServerQueueCodes:
                continue
            
            if userName in line and hostName in line:
                # running job                    
                if '@' in line:
                    # identify license server
                    licenseServer = licenseServerQueueCodes[licenseServerQueueCode]
                    noOfTokens = int(parts[-1].split('=')[-1])
                    return licenseServer, noOfTokens 
                
        return None, 0
    
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
    def getFree(cls):
        
        freeTokens = 0
        freeLicenseServer = None
        for licenseServer in LICENSE_SERVER_TYPES:
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
#     licenseServerTypes = None
    
    #-------------------------------------------------------------------------
    
    def __init__(self, name, fullName):
        
        self.name = name
        self.fullName = fullName
        
        self.infoLine = ''
        
        self.runningJobs = dict()
        self.freeCpuNo = self.NO_OF_CORES
        self.isUserMachine = False
        
        self._identityUserMaschine()
        self._checkRunningJobs()
        
    #-------------------------------------------------------------------------
    
    def _checkRunningJobs(self):
        
        usedCpuNo = 0
        for jobId, attrs in self.getRuningJobs().iteritems():
            licenceServer, noOfTokens = BaseLicenseServerType.getUserTokenStatus(
                attrs['job_owner'], self.name)
            
            # in case of job running for a different solver
            if licenceServer is None:
                continue
            
            noOfCpus = licenceServer.getNoOfCpus(noOfTokens)
            attrs['used_cpus'] = noOfCpus
            attrs['licenceServer'] = licenceServer
            attrs['used_tokens'] = noOfTokens
            usedCpuNo += noOfCpus
            
            self.runningJobs[jobId] = attrs
        
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
    
    def getInfoLine(self):
                 
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
        
        for jobId, attrs in self.runningJobs.iteritems():
            self.infoLine += '\n\tRunning job: %s (%s uses %s %s tokens %s CPUs)' % (
                jobId, attrs['job_owner'], attrs['used_tokens'], attrs['licenceServer'].NAME, attrs['used_cpus'])
        
        # highlight user machine        
        if self.isUserMachine:
            self.infoLine = utils.ConsoleColors.OKBLUE + self.infoLine + utils.ConsoleColors.ENDC
                       
        return self.infoLine
    
#     #-------------------------------------------------------------------------
#     @classmethod
#     def connectLicenseServerTypes(cls, licenseServerTypes):
#         
#         cls.licenseServerTypes = licenseServerTypes
        
    #-------------------------------------------------------------------------
    @classmethod
    def connectResources(cls):
        
        cls.resources = ServerResources()
    
    #-------------------------------------------------------------------------
    @classmethod
    def getDescription(cls):
        
        return '%s (%s cores, %s GPU, %s, free cores:N/A)' % (
            cls.NAME, cls.NO_OF_CORES, cls.NO_OF_GPU, cls.DESCRIPTION)
    
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
    
    #-------------------------------------------------------------------------
    
    def _getAvailableLicenses(self):
                
        return LICENSE_SERVER_TYPES[:3]
    
    #-------------------------------------------------------------------------
    
    def getSelection(self):
        
        licenseServerList = self._getAvailableLicenses()
        
        options = list()
        for licenseServer in licenseServerList:
            status = licenseServer.getTokenStatus()
            options.append('%s %s license (free tokens: %s/%s)' % (
                licenseServer.LICENSE_TYPE.NAME, licenseServer.NAME, status['free'], status['total']))
        
        # print list of servers
        index = self._getOptionFromList(
            'Available license servers',
            "Enter the number which represent ABAQUS queue [enter=%s]: " % self.DFT_OPTION_INDEX,
            options)
        
        return licenseServerList[index]
    
#==============================================================================

class InputFileSelector(BaseDataSelector):
    
    FILE_EXT = ei.FileExtensions.ABAQUS_INPUT
    
    def __init__(self, parentApplication, workDir):
        super(InputFileSelector, self).__init__(parentApplication)
        
        self.workDir = workDir
                
    #--------------------------------------------------------------------------

    def getSelection(self):
        
        inpFiles = glob.glob(os.path.join(self.workDir, '*%s' % self.FILE_EXT))
        
        # select input file
        if len(inpFiles) == 0:
            raise DataSelectorException("Error: source *%s wasn't found!" % self.FILE_EXT)
        elif len(inpFiles) == 1:
            return inpFiles
        else:
            indexes = self._getOptionFromList('Available input files',
                'Select input file(s) No. [1 or 1 2 ..., enter=%s, a=all]: ' % self.DFT_OPTION_INDEX,
                [os.path.basename(inpFileName) for inpFileName in inpFiles],
                multiSelection=True)
            
            return [inpFiles[index] for index in indexes]
            
#==============================================================================

class RestartInputFileSelector(InputFileSelector):
            
    def getSelection(self):
        
        inpFiles = glob.glob(os.path.join(self.workDir, '*%s' % self.FILE_EXT))
        
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

class PamcrashInputFileSelector(InputFileSelector):
    
    FILE_EXT = ei.FileExtensions.PAMCRASH_INPUT
    
#==============================================================================

class SolverVersionSelector(BaseDataSelector):
    
    DFT_OPTION_INDEX = 3
      
    #--------------------------------------------------------------------------
    
    def _getAvailableVersions(self):

#TODO: load dynamically?
        
        versions = ei.ABAQUS_SOLVER_LIST
        
        return versions
    
    #--------------------------------------------------------------------------

    def getSelection(self):
        
        index = self._getOptionFromList(
            'Choose the ABAQUS solver version',
            'Enter number which represent version of solver[enter=%s]: ' % self.DFT_OPTION_INDEX,
            self._getAvailableVersions())
            
        return self._getAvailableVersions()[index]

#==============================================================================

class ExecutionServerSelector(BaseDataSelector):
    
    DFT_OPTION_INDEX = 2
    
    #--------------------------------------------------------------------------
    
    def getAvailableHosts(self):
        
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
            infoLines.append(host.getInfoLine())
                
        return allHosts, infoLines, serverHosts, userHosts
        
    #--------------------------------------------------------------------------

    def getSelection(self):
        
        hosts, infoLines, serverHosts, userHosts = self.getAvailableHosts()
        
        self.printSelectionTitle('Choose the execution host')
        
        description = 'Info - your computer is: %s' % self.parentApplication.profile.user.machine
        
        # server type overview        
        for server in serverHosts:
            description += '\n\t%s (%s cores, %s GPU, %s, free cores: %s)' % (
                server.NAME, server.NO_OF_CORES, server.NO_OF_GPU, server.DESCRIPTION,
                server.freeCpuNo)
        
        description += '\n\t%s' % WorkstationExecutionServerType.getDescription()
        
        description += '\nAvailable execution hosts for this queue'
        description += '\n' + 80*'-'
        description += '\nqueuename                      qtype resv/used/tot. load_avg    arch       states'
        description += '\n' + 80*'-'
        
        index = self._getOptionFromList(description, 
            "Enter the number which represent prefered execution host [enter=%s]: " % self.DFT_OPTION_INDEX,
            infoLines)
                        
        return hosts[index]

#==============================================================================

class PamCrashExecutionServerSelector(ExecutionServerSelector):
    
    DFT_OPTION_INDEX = 3
    
#==============================================================================

class User(object):
    
    def __init__(self):
        
        self.name, self.machine, self.email = utils.getUserInfo()

#==============================================================================

class ServerResources(object):
    
    def __init__(self):
        
        self._hostsStat = dict()
        
        self.updateHostStat()
    
    #--------------------------------------------------------------------------
    
    def updateHostStat(self):
        
        self._hostsStat = xmlio.GridEngineInterface.getHostsStat()
    
    #--------------------------------------------------------------------------
    
    def getHostStat(self, hostName):
                
        if hostName not in self._hostsStat:
            raise xmlio.GridEngineInterfaceException('Unknown host name: %s' % hostName)
        
        return self._hostsStat[hostName]
    
#==============================================================================

class RunningJob(object):
    
    COLUMNS_WIDTHS = [6, 9, 12, 55, 4, 21, 25, 7, 6]
    
    def __init__(self, attributes):
                
        
        self._attributes = attributes
        
        if self._attributes['queue_name'] is not None:            
            self.executionServer = BaseExecutionServerType.getServerFromName(
                self._attributes['queue_name'])
        else:
            self.executionServer = None
    
    #--------------------------------------------------------------------------
    
    def __getitem__(self, attributeName):
        
        if attributeName in self._attributes:
            return self._attributes[attributeName]
        else:
            return None
    
    #--------------------------------------------------------------------------
    
    def toString(self):
        
        lineFormat = ['{:>%s}' % w for w in self.COLUMNS_WIDTHS]
        
        string = ''
        jobtime='not set'
        if self._attributes['state'] == 'r':
                jobtime = self._attributes['JAT_start_time']
        elif self._attributes['state'] == 'dt':
                jobtime = self._attributes['JAT_start_time']
        else:
                jobtime = self._attributes['JB_submission_time']
        
        queueName = self._attributes['queue_name']
        if queueName is None:
            queueName = ''
        
        string += '\n'+ ''.join(lineFormat).format(
            self._attributes['JB_job_number'], self._attributes['JAT_prio'],
            self._attributes['JB_owner'], self._attributes['JB_name'],
            self._attributes['state'], jobtime, queueName,
            self._attributes['hard_request'], self._attributes['slots'])
        
#         if self.executionServer is not None:
#             print self.executionServer.freeCpuNo
                
        return string
        
#==============================================================================

class Queue(object):
    
    COLUMN_LABELS = ["JOB-ID","priority","user","job-name","st",
        "submit/start_at","queue name",'tokens', "slots"]
    
    def __init__(self):
        
        self.jobs = list()
        
        self.updateState()
    
    #--------------------------------------------------------------------------
    
    def updateState(self):
        
        jobAttributes = xmlio.GridEngineInterface.getQueueStat()
        
        self.jobs = list()
        for jobAttribute in jobAttributes: 
            self.jobs.append(RunningJob(jobAttribute))
            
    #--------------------------------------------------------------------------
    
    def __repr__(self):
        
        self.updateState()
        
        string = ''
        lineFormat = ['{:>%s}' % w for w in RunningJob.COLUMNS_WIDTHS]
        string += ''.join(lineFormat).format(*self.COLUMN_LABELS)
        string += '\n'+ 150*'-'
        
        for job in self.jobs:
            string += job.toString()
        
        return string
    
    
