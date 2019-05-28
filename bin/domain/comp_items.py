#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Python script for '''

import os
import sys
import time
import copy
import shutil
import subprocess
import logging
import tempfile

import utils
import base_items as bi
import enum_items as ei
from persistent import file_items as fi
from interfaces import xmlio

#==============================================================================

ABAQUS_EXECUTION_PROFILE_TYPES = list()
PAMCRASH_EXECUTION_PROFILE_TYPES = list()

#==============================================================================

class AbaqusJob(object):
    
    DFT_PRIORITY = 50
    EXECUTABLE_FILE_TYPE = fi.AbaqusJobExecutableFile
    
    def __init__(self):
        
        self.inpFile = None
        self.description = '-'
        self.startTime = time.strftime('%m%d%H%M')
        self.numberOfCores = 1
        self.numberOfGPUCores = 0
        self.priority = self.DFT_PRIORITY
        self.solverVersion = ''
        
        self.restartInpFile = None
        self.executableFile = None

#TODO: check this!
        # for datacheck case
        self.fixTokenNumber = None
    
    #--------------------------------------------------------------------------
    
    def setInpFile(self, inpFileName):
        
        self.inpFile = fi.AbaqusInpFile(inpFileName)
    
    #--------------------------------------------------------------------------
    
    def setRestartInpFile(self, inpFileName):
        
        self.restartInpFile = fi.AbaqusInpFile(inpFileName)
        fileNames = self.restartInpFile.getExistingAnalysisFileNames()
        
        info = dict()
        for fileName in fileNames:
            baseName = os.path.basename(fileName)
            destName = os.path.join(self.inpFile.dirName, baseName)
            
            if os.path.exists(destName):
#                 raise bi.InputFileSelector(
                print 'File for restart already exists in the project folder! Skipping the copy process.'
                info[baseName] = 'File already present.'
            else:
                print 'Copying "%s" file for restart to: "%s"' % (
                    baseName, destName)                
                shutil.copy(fileName, destName)
                info[baseName] = 'File copied.'
        
        return info
                
    #--------------------------------------------------------------------------
    
    def setDescription(self, text):
        
        if len(text) > 15:
            text = text[:15]
        
        self.description = text
        
        logging.info('Job description set to: %s' % self.description)
        
    #--------------------------------------------------------------------------
    
    def setStartTime(self, startTime):
        
        self.startTime = startTime
        
        logging.info('Job start time set to: %s' % self.startTime)
    
    #--------------------------------------------------------------------------
    
    def setNumberOfCores(self, numberOfCores):
        
        self.numberOfCores = numberOfCores
        
        logging.info('Number of CPU set to: %s' % self.numberOfCores)
    
    #--------------------------------------------------------------------------
    
    def setNumberOfGPUCores(self, numberOfGPUCores):
        
        self.numberOfGPUCores = numberOfGPUCores
        
        logging.info('Selected GPGPU acceleration: %s' % self.numberOfGPUCores)
    
    #--------------------------------------------------------------------------
    
    def setPriority(self, priority):
                
        logging.info('Job priority set to: %s (-> %s)' % (priority, priority - 100))
        
        self.priority = priority - 100
    
    #--------------------------------------------------------------------------
    
    def setSolverVersion(self, solverVersion):
        
        self.solverVersion = solverVersion
        
        logging.info('Selected version: %s' % self.solverVersion)
            
    #--------------------------------------------------------------------------
    
    def getTokensRequired(self):
        
        if self.fixTokenNumber is not None:
            return self.fixTokenNumber
        
        tokensRequired = 0
        
#         # for any other calculation then perturbation there is 4 tokens required
#         if not self.inpFile.stepPerturbation:
#             tokensRequired += 4
        
        # obtain number of tokens according to number of cores
        tokensRequired += bi.DslsLicenseType.getNoOfTokens(self.numberOfCores)

#TODO: wtf???
#         # reduce number of tokens in case of GPU usage
#         if self.numberOfGPUCores:
#             tokensRequired -= 5
        
        return tokensRequired
    
    #--------------------------------------------------------------------------
    
    def setExecutableFile(self, executableFile):
        
        self.executableFile = executableFile
    
    #--------------------------------------------------------------------------
    
    def getCopy(self):
        
        return copy.deepcopy(self)
    

#==============================================================================

class PamCrashJob(AbaqusJob):
      
    EXECUTABLE_FILE_TYPE = fi.PamCrashJobExecutableFile
    
    def setInpFile(self, inpFileName):
        
        self.inpFile = fi.PamCrashInpFile(inpFileName)
        
    #--------------------------------------------------------------------------
    
    def getTokensRequired(self):
        
        if self.fixTokenNumber is not None:
            return self.fixTokenNumber
        
        tokensRequired = 0
        
        # obtain number of tokens according to number of cores
        tokensRequired += bi.PamcrashLicenseType.getNoOfTokens(self.numberOfCores)
        
        return tokensRequired
       
#==============================================================================

class JobExecutionSetting(object):
    
    SCRATCH_PATH = '/scr1/scratch/grid'
    SCRATCH_SERVER_PATH = '/scr1/tmp'
    
    def __init__(self):
        
        self.licenseServer = None
        self.executionServer = None
        self.additionalSolverParams = ''
    
    #--------------------------------------------------------------------------
    
    def setLicenseServer(self, licenseServer):
        
        self.licenseServer = licenseServer
        
        logging.info('Selected license: %s' % self.licenseServer.NAME)
    
    #--------------------------------------------------------------------------
    
    def setExecutionServer(self, executionServer):
        
        self.executionServer = executionServer
        
        logging.info('Selected host: %s' % self.executionServer.name)
    
    #--------------------------------------------------------------------------
    
    def setAdditionalSolverParams(self, params):
        
        if len(params) > 15:
            logging.warning('Warning: not all parameters parsed! %s -> %s' % (params, params[:15]))
            params = params[:15]
            
        self.additionalSolverParams = params
        
        logging.info('Additional solver parameters set to: %s' % self.additionalSolverParams)
    
#==============================================================================

class BaseExecutionProfileType(object):

    container = ABAQUS_EXECUTION_PROFILE_TYPES
    SOLVER_TYPE = bi.AbaqusSolverType

    def __init__(self, parentApplication):
        
        self.parentApplication = parentApplication
        self.job = AbaqusJob()
        self.jobSettings = JobExecutionSetting()
        self.user = User()
        
        self.inpFileNames = list()
                
    #--------------------------------------------------------------------------
    
    def runDataSelectionSequence(self):
        
        self._setInputFile()
        self._setLicenseServer()
        self._setSolverVersion()
        self._setExecutionServer()
        self._setNumberOfCores()
        self._setNumberOfGPUCores()
        self._setJobPriority()
        self._setJobStartTime()
        self._setJobDescription()
        self._setAdditionalSolverParams()
        
        logging.info("Info- Required licenses for this job are: %s" % self.job.getTokensRequired())
        
    #--------------------------------------------------------------------------

    def _setInputFile(self, inpFileNames=None):
        
        # switch between parametric and interactive input
        if inpFileNames is not None:
            self.inpFileNames = inpFileNames
        else:
            inpSelector = bi.InputFileSelector(self.parentApplication)
            self.inpFileNames = inpSelector.getSelection()
                    
        self.job.setInpFile(self.inpFileNames[0])
        
        logging.info('Selected file(s): %s' % ', '.join([
            os.path.basename(inpFileName) for inpFileName in self.inpFileNames]))
        
        filesNeedingRestart = list()
        for inpFileName in self.inpFileNames:
            inpFile = fi.AbaqusInpFile(inpFileName)
            if inpFile.subAllFiles:
                filesNeedingRestart.append(inpFile)
        
        if len(filesNeedingRestart) > 0:
            raise bi.DataSelectorException('Use GUI version to handle restart simulation option.')
#TODO: finish this if it's needed..            
#         # in case of restart read
#         if self.job.inpFile.subAllFiles:
#             inpSelector = bi.RestartInputFileSelector(self.parentApplication)
#             restartInpFileName = inpSelector.getSelection()
#             
#             self.job.setRestartInpFile(restartInpFileName)
#             
#             print '\tSelected restart file: %s' % restartInpFileName
                    
    #--------------------------------------------------------------------------

    def _setLicenseServer(self):
        
        licenseSelector = bi.LicenseServerSelector(self.parentApplication)
        licenseSelector.DFT_OPTION_INDEX = self.getDftLicenseServerOption()
        licenseServer = licenseSelector.getSelection()
    
        self.jobSettings.setLicenseServer(licenseServer)
        
    #--------------------------------------------------------------------------
    
    def _setSolverVersion(self):
        
        solverVersionSelector = bi.SolverVersionSelector(self.parentApplication)
        solverVersion = solverVersionSelector.getSelection()
        solverVersionPath = solverVersionSelector.VERSIONS.getSolverPath(solverVersion) 
        
        self.job.setSolverVersion(solverVersionPath)
        
    #--------------------------------------------------------------------------
    
    def _setExecutionServer(self):
        
        hostSelector = bi.ExecutionServerSelector(self.parentApplication)
        hostSelector.DFT_OPTION_INDEX = self.getDftExectionServerOption()
        executionServer = hostSelector.getSelection()
        
        self.jobSettings.setExecutionServer(executionServer)
        
    #--------------------------------------------------------------------------
    
    def _setJobDescription(self):
        
        bi.BaseDataSelector.printSelectionTitle('Job description')
        
        jobDescription = bi.BaseDataSelector.getTextInput(
            'Enter description of job [15 characters, enter="-"]: ', '-')
                
        self.job.setDescription(jobDescription)
    
    #--------------------------------------------------------------------------
    
    def _setJobStartTime(self):
        
        bi.BaseDataSelector.printSelectionTitle('Job start time')
        
        jobStartTime = bi.BaseDataSelector.getTimeInput(
            'Enter deferred time of computation [MMDDhhmm, enter=put ASAP into queue]: ',
            self.job.startTime)
        
        self.job.setStartTime(jobStartTime)
            
    #--------------------------------------------------------------------------
    
    def _setNumberOfCores(self):
        
        minValue, maxValue, dftValue = self.getDftNoOfCores()
        
        numberOfCores = bi.BaseDataSelector.getIntInput('Choose the number of CPU', 
            'Enter number of CPU cores [max %s, enter=%s]: ' % (
                maxValue, dftValue),
            minValue, maxValue, dftValue)
        
        self.job.setNumberOfCores(numberOfCores)
    
    #--------------------------------------------------------------------------
    
    def _setNumberOfGPUCores(self):        
                
        minValue, maxValue, dftValue = self.getDftNoOfGpus()
        
        if maxValue > 0:
            numberOfGPUCores = bi.BaseDataSelector.getIntInput('Choose the number of GPU', 
                'Enter number of NVIDIA GPU acceleration [max %s, enter=%s]: ' % (
                    maxValue, dftValue),
                dftValue=dftValue,
                maxValue=maxValue)
        else:
            numberOfGPUCores = 0
        
        self.job.setNumberOfGPUCores(numberOfGPUCores)
            
    #--------------------------------------------------------------------------
    
    def _setJobPriority(self):        
        
        minValue, maxValue, dftValue = self.getDftJobPriority()
        
        priority = bi.BaseDataSelector.getIntInput('Choose job priority', 
            'Enter priority in the queue [%s-%s, enter=%s]: ' % (
                minValue, maxValue, dftValue),
            minValue=minValue, maxValue=maxValue, dftValue=dftValue)
          
        self.job.setPriority(priority)
    
    #--------------------------------------------------------------------------
    
    def _setAdditionalSolverParams(self):
        
        bi.BaseDataSelector.printSelectionTitle('Additional parameters for solver')
        
        params = bi.BaseDataSelector.getTextInput(
            'Specify more job parameters [15 characters, enter=none]: ', '')
        
        self.jobSettings.setAdditionalSolverParams(params)
    
    #--------------------------------------------------------------------------

    def getDftLicenseServerOption(self):
                
        return bi.LicenseServerSelector.DFT_OPTION_INDEX

    #--------------------------------------------------------------------------

    def getDftNoOfCores(self):   
    
        maxValue = self.jobSettings.executionServer.NO_OF_CORES
        minValue = 1
        dftValue = self.jobSettings.executionServer.getDftCoreNumber()
        
        return minValue, maxValue, dftValue
    
    #--------------------------------------------------------------------------

    def getDftNoOfGpus(self):
    
        # skip an option to chose GPU for explicit calculation
        if self.job.inpFile.dynamicsExplicit:
            logging.info("GPGPU acceleration is NOT AVAILABLE")
            return 0, 0, 0
        elif self.jobSettings.executionServer.NO_OF_GPU == 0:
            logging.info("GPGPU acceleration is NOT AVAILABLE")
            return 0, 0, 0
                
        return 0, self.jobSettings.executionServer.NO_OF_GPU, 0
        
    #--------------------------------------------------------------------------
    
    def getDftExectionServerOption(self):
        
        return bi.ExecutionServerSelector.DFT_OPTION_INDEX
    
    #--------------------------------------------------------------------------
    
    def getDftJobPriority(self):
        
        return 40, 60, self.job.DFT_PRIORITY
        
#==============================================================================
@utils.registerClass
class DatacheckExecutionProfileType(BaseExecutionProfileType):
    
    NAME = 'Datacheck - start immediately (1 CPU on local workstation)'
    ID = 2
    
    DATACHECK_CPU_NO = 1
    DATACHECK_TOKEN_NO = 30
        
    #--------------------------------------------------------------------------

    def _setLicenseServer(self):
        
        self.job.setNumberOfCores(self.DATACHECK_CPU_NO)
        self.job.fixTokenNumber = self.DATACHECK_TOKEN_NO

#TODO: fix token number for datacheck
#         tokensRequired = bi.DslsLicenseType.getNoOfTokens(self.job.numberOfCores)
        tokensRequired = self.DATACHECK_TOKEN_NO
        licenseServer = bi.BaseLicenseServerType.getFreeFromTokens(tokensRequired)
        
        self.jobSettings.setLicenseServer(licenseServer)
    
    #--------------------------------------------------------------------------

    def _setExecutionServer(self):
        
        # find user workstation
        for host in self.jobSettings.licenseServer.getAvailableHosts():
            if host.isUserMachine:
                executionServer = host
                break
        
        self.jobSettings.setExecutionServer(executionServer)
    
    #--------------------------------------------------------------------------

    def _setAdditionalSolverParams(self):
        
        self.jobSettings.setAdditionalSolverParams(' datacheck')
    
    #--------------------------------------------------------------------------

    def _setJobDescription(self):
        
        self.job.setDescription('datacheck')
    
    #--------------------------------------------------------------------------
        
    def _setJobStartTime(self): pass
    
    #--------------------------------------------------------------------------
    
    def _setNumberOfCores(self): pass
    
    #--------------------------------------------------------------------------

    def _setNumberOfGPUCores(self): pass
    
    #--------------------------------------------------------------------------
    
    def _setJobPriority(self): pass
    
    #--------------------------------------------------------------------------
    
    def getDftNoOfCores(self):
                        
        return 1, 1, 1

    #--------------------------------------------------------------------------
    
    def getDftExectionServerOption(self):
        
        hostSelector = bi.ExecutionServerSelector(self.parentApplication)
        hosts, infoLines, serverHosts, userHosts, description = hostSelector.getOptions()
        
        # check available AP host
        for host in userHosts:    
            if host.isUserMachine:
                return hosts.index(host) + 1
        
        return 1
        
    
#==============================================================================
@utils.registerClass
class LicensePriorityExecutionProfileType(BaseExecutionProfileType):
    
    NAME = 'License priority - use any free license (reduce CPU and start on any free server)'
    ID = 0
    
    #--------------------------------------------------------------------------

    def _getPreferredNumberOfCpus(self):
        
        status = self.jobSettings.licenseServer.getTokenStatus()
        defaultNoOfCores = self.jobSettings.licenseServer.getNoOfCpus(int(status['free']))
        
        return defaultNoOfCores
    
    #--------------------------------------------------------------------------

    def getDftLicenseServerOption(self):
        
        freeLicenseServer = bi.BaseLicenseServerType.getFree(self.SOLVER_TYPE.NAME)
        if freeLicenseServer is None:
            return bi.LicenseServerSelector.DFT_OPTION_INDEX
        else:
            return bi.LICENSE_SERVER_TYPES.index(freeLicenseServer) + 1
    
#     #--------------------------------------------------------------------------
# 
#     def _setLicenseServer(self):
#                         
#         licenseSelector = bi.LicenseServerSelector(self.parentApplication)
#         licenseSelector.DFT_OPTION_INDEX = self.getDftLicenseServerOption()
#         licenseServer = licenseSelector.getSelection()
#         
#         self.jobSettings.setLicenseServer(licenseServer)

    #--------------------------------------------------------------------------
    
    def getDftExectionServerOption(self):
        
        availableHost = None
        defaultNoOfCores = self._getPreferredNumberOfCpus()
        
        hostSelector = bi.ExecutionServerSelector(self.parentApplication)
        hosts, infoLines, serverHosts, userHosts, description = hostSelector.getOptions()
        
        # check available AP host
        for host in serverHosts:
            if host.freeCpuNo >= defaultNoOfCores or (
                defaultNoOfCores >= host.NO_OF_CORES and host.freeCpuNo == host.NO_OF_CORES):
                availableHost = host
                break
        
        # check available user workstation
        if availableHost is None:
            for host in userHosts:
                if host.isUserMachine:
                    if len(host.runningJobs) == 0:
                        availableHost = host
                    break
        
        # check first free user workstation
        if availableHost is None:
            for host in userHosts:
                if len(host.runningJobs) == 0:
                    availableHost = host
                    break
        
        return hosts.index(availableHost) + 1
    
    #--------------------------------------------------------------------------
    
#     def _setExecutionServer(self):
#         
#         availableHost = None
#         defaultNoOfCores = self._getPreferredNumberOfCpus()
#         
#         hostSelector = bi.ExecutionServerSelector(self.parentApplication)
#         hosts, infoLines, serverHosts, userHosts = hostSelector.getOptions()
#         
#         # check available AP host
#         for host in serverHosts:    
#             if host.freeCpuNo > defaultNoOfCores:
#                 availableHost = host
#                 break
#         
#         # check available user workstation
#         if availableHost is None:
#             for host in userHosts:
#                 if host.isUserMachine:
#                     if len(host.runningJobs) == 0:
#                         availableHost = host
#                     break
#         
#         # check first free user workstation
#         if availableHost is None:
#             for host in userHosts:
#                 if len(host.runningJobs) == 0:
#                     availableHost = host
#                     break
#         
#         # set new default option value
#         hostSelector.DFT_OPTION_INDEX = hosts.index(availableHost) + 1
#         executionServer = hostSelector.getSelection()
#         
#         self.jobSettings.setExecutionServer(executionServer)
        
    #--------------------------------------------------------------------------
    
#     def _setNumberOfCores(self):
#         
#         defaultNoOfCores = self._getPreferredNumberOfCpus()
#         
#         if defaultNoOfCores > self.jobSettings.executionServer.NO_OF_CORES:
#             defaultNoOfCores = self.jobSettings.executionServer.NO_OF_CORES
#                 
#         numberOfCores = bi.BaseDataSelector.getIntInput('Choose the number of CPU', 
#             'Enter number of CPU cores [max %s, enter=%s]: ' % (
#                 self.jobSettings.executionServer.NO_OF_CORES, defaultNoOfCores),
#             maxValue = self.jobSettings.executionServer.NO_OF_CORES,
#             minValue = 1,
#             dftValue = defaultNoOfCores)
#         
#         self.job.setNumberOfCores(numberOfCores)
    
    #--------------------------------------------------------------------------
    
    def getDftNoOfCores(self):
        
        defaultNoOfCores = self._getPreferredNumberOfCpus()
        
        if defaultNoOfCores >= self.jobSettings.executionServer.NO_OF_CORES:
            defaultNoOfCores = self.jobSettings.executionServer.getDftCoreNumber()
        
        minValue = 1
        maxValue = self.jobSettings.executionServer.NO_OF_CORES
                
        return minValue, maxValue, defaultNoOfCores
        
#==============================================================================
@utils.registerClass
class ResourcePriorityExecutionProfileType(BaseExecutionProfileType):
    
    NAME = 'Resource priority - wait for free license (use max. CPU on preferred server)'
    ID = 1

#==============================================================================

class AbaqusExecutionProfileSelector(bi.BaseDataSelector):
    
    DFT_OPTION_INDEX = 1
    DESCRIPTION = 'Select execution profile'
    
    profiles = ABAQUS_EXECUTION_PROFILE_TYPES
    
    #--------------------------------------------------------------------------
    
    def getOptions(self):
        
        return [profileType.NAME for profileType in self.profiles]
    
    #--------------------------------------------------------------------------
    
    def indexToItem(self, index):
        
        return self.profiles[index]

    #--------------------------------------------------------------------------

    def getSelection(self):
        
        options = self.getOptions()
        
        index = self._getOptionFromList(
            self.DESCRIPTION,
            'Enter execution profile number [enter=%s]: ' % self.DFT_OPTION_INDEX,
            options)
            
        return self.indexToItem(index)
        
#==============================================================================
@utils.registerClass
class PamCrashExecutionProfileType(BaseExecutionProfileType):
    
    container = PAMCRASH_EXECUTION_PROFILE_TYPES
    SOLVER_TYPE = bi.AbaqusSolverType
    
    NAME = 'PamCrash analysis'
    ID = 0
        
    def __init__(self, parentApplication):
        
        self.parentApplication = parentApplication
        self.job = PamCrashJob()
        self.jobSettings = JobExecutionSetting()
        self.user = User()
        
        self.inpFileNames = list()
        
    #--------------------------------------------------------------------------

    def _setInputFile(self):
        
        inpSelector = bi.PamcrashInputFileSelector(self.parentApplication)
        self.inpFileNames = inpSelector.getSelection()
        
        self.job.setInpFile(self.inpFileNames[0])
        
        logging.info('Selected file(s): %s' % ', '.join([
            os.path.basename(inpFileName) for inpFileName in self.inpFileNames]))
        
    #--------------------------------------------------------------------------

    def _setLicenseServer(self):
        
        bi.BaseDataSelector.printSelectionTitle('Available license servers')
        
        licenseServer = bi.PamCrashLicenseServerType
        
        logging.info(licenseServer.toOptionLine())
       
        self.jobSettings.setLicenseServer(licenseServer)

    #--------------------------------------------------------------------------
    
    def _setSolverVersion(self):
        
#         solverVersion = ei.PAMCRASH_SOLVER_LIST[0]
        solverVersionSelector = bi.PamCrashSolverVersionSelector(self.parentApplication)
        solverVersion = solverVersionSelector.getSelection()
        solverVersionPath = solverVersionSelector.VERSIONS.getSolverPath(solverVersion) 
        
        self.job.setSolverVersion(solverVersionPath)
        
    #--------------------------------------------------------------------------
    
    def _setExecutionServer(self):
        
        hostSelector = bi.PamCrashExecutionServerSelector(self.parentApplication)
        executionServer = hostSelector.getSelection()
        
        self.jobSettings.setExecutionServer(executionServer)        
               
    #--------------------------------------------------------------------------
    
#     def _setNumberOfGPUCores(self):        
#         
#         # skip an option to chose GPU for explicit calculation
#         if self.job.inpFile.analysisType == ei.AnalysisTypes.EXPLICIT:
#             self.job.setNumberOfGPUCores(0)
#             print "\tGPGPU acceleration is NOT AVAILABLE"
#             return
#         elif self.jobSettings.executionServer.NO_OF_GPU == 0:
#             print "\tGPGPU acceleration is NOT AVAILABLE"
#             return
#         
#         numberOfGPUCores = bi.BaseDataSelector.getIntInput('Choose the number of GPU', 
#             'Enter number of NVIDIA GPU acceleration [max %s, enter=%s]: ' % (
#                 self.jobSettings.executionServer.NO_OF_GPU, 0),
#             dftValue=0,
#             maxValue=self.jobSettings.executionServer.NO_OF_GPU)
#         
#         self.job.setNumberOfGPUCores(numberOfGPUCores)

    #--------------------------------------------------------------------------

    def _getPreferredNumberOfCpus(self):
        
        status = self.jobSettings.licenseServer.getTokenStatus()
        defaultNoOfCores = self.jobSettings.licenseServer.getNoOfCpus(int(status['free']))
        
        return defaultNoOfCores
    
    #--------------------------------------------------------------------------
    
    def getDftExectionServerOption(self):
        
        return bi.PamCrashExecutionServerSelector.DFT_OPTION_INDEX
    
    #--------------------------------------------------------------------------
    
    def getDftNoOfCores(self):
        
        defaultNoOfCores = self._getPreferredNumberOfCpus()
        
        if defaultNoOfCores >= self.jobSettings.executionServer.NO_OF_CORES:
            defaultNoOfCores = self.jobSettings.executionServer.getDftCoreNumber()
        
        minValue = 1
        maxValue = self.jobSettings.executionServer.NO_OF_CORES
                
        return minValue, maxValue, defaultNoOfCores
    
    #--------------------------------------------------------------------------

    def getDftNoOfGpus(self):
    
        # skip an option to chose GPU for explicit calculation
        if self.job.inpFile.analysisType == ei.AnalysisTypes.EXPLICIT:
            logging.info("GPGPU acceleration is NOT AVAILABLE")
            return 0, 0, 0
        elif self.jobSettings.executionServer.NO_OF_GPU == 0:
            logging.info("GPGPU acceleration is NOT AVAILABLE")
            return 0, 0, 0
                
        return 0, self.jobSettings.executionServer.NO_OF_GPU, 0
        
#==============================================================================
@utils.registerClass
class PamCrashDataCheckExecutionProfileType(PamCrashExecutionProfileType):
        
    NAME = 'Datacheck'
    ID = 1

    DATACHECK_CPU_NO = 1
    DATACHECK_TOKEN_NO = 0
        
    #--------------------------------------------------------------------------

    def _setLicenseServer(self):
        
        self.job.setNumberOfCores(self.DATACHECK_CPU_NO)
        self.job.fixTokenNumber = self.DATACHECK_TOKEN_NO
        
        licenseServer = bi.PamCrashLicenseServerType    
        self.jobSettings.setLicenseServer(licenseServer)
        
    #--------------------------------------------------------------------------

    def _setAdditionalSolverParams(self): pass
    
    #--------------------------------------------------------------------------

    def _setJobDescription(self):
        
        self.job.setDescription('datacheck')
    
    #--------------------------------------------------------------------------
        
    def _setJobStartTime(self): pass
    
    #--------------------------------------------------------------------------
    
    def _setNumberOfCores(self): pass
    
    #--------------------------------------------------------------------------

    def _setNumberOfGPUCores(self): pass
    
    #--------------------------------------------------------------------------
    
    def _setJobPriority(self): pass


#==============================================================================

class PamCrashExecutionProfileSelector(AbaqusExecutionProfileSelector):
    
    DFT_OPTION_INDEX = 1
    profiles = PAMCRASH_EXECUTION_PROFILE_TYPES

#==============================================================================

class User(object):
    
    def __init__(self):
        
        self.name, self.machine, self.email = utils.getUserInfo()

#==============================================================================

class Resources(object):
    
    QLIC_COMMAND = 'qlic'
    QLIC_COUMNS = ['resource', 'total', 'limit', 'extern', 'intern', 'wait', 'free']
    
    executionServers = dict()
    availableLicenseServerHosts = dict()
    jobsInQueue = dict()
#     jobsOutQueue = dict()
    tokenStatus = dict()
    
    _hostsStat = dict()
    _outOfQueueJobIds = list()
    
#     def __init__(self):
#                 
#         self.updateHostStat()
    
    #--------------------------------------------------------------------------
    @classmethod
    def initialise(cls):
        
        cls._setupResources()
        
        cls._setupJobsInQueue()
        cls._setupExecutionServers()
        cls._setAvailableHosts()
        cls._getTokenStatus()
        
#         print cls.executionServers
#         print cls.availableLicenseServerHosts
#         print cls.jobsInQueue
#         print cls.tokenStatus
    
    #--------------------------------------------------------------------------
    @classmethod
    def updateState(cls):
        
        cls._setupJobsInQueue()
        cls._updateHostStat()
        cls._getTokenStatus()
        
    #--------------------------------------------------------------------------
    @classmethod
    def _setupResources(cls):
        
        for licenceServer in bi.LICENSE_SERVER_TYPES:
            licenceServer.connectResources(cls)
        
        bi.BaseExecutionServerType.connectResources(cls)
        Queue.connectResources(cls)
        
    #--------------------------------------------------------------------------
    @classmethod
    def _updateHostStat(cls):
        
        cls._hostsStat = xmlio.GridEngineInterface.getHostsStat()
        
    #--------------------------------------------------------------------------
    @classmethod
    def _getOutOfQueueJobsStat(cls):
        
        '''
        qhost:
            hostName = mb-u24.cax.lan
        
        qlic -w:
            pamcrash1  ext.opawar=[33]
                       ext.opawar@mb-so3=33
                       stekly=[66]
            qxt3       bouda@mb-u15=50
        
        '''
        
        # check jobs running out of the queue
        stdout, _ = utils.runSubprocess('qlic -w')
        lines = stdout.splitlines()
        
        licenseServerQueueCodes = dict()
        for licenseServer in bi.LICENSE_SERVER_TYPES:
            licenseServerQueueCodes[licenseServer.QUEUE_CODE] = licenseServer
        
        outOfQueueJobsParams = list()
        for line in lines:
            parts = line.split()
            if len(parts) == 2 and parts[0]:
                licenseServerQueueCode = parts[0].strip()
                             
            # skip different queues
            if licenseServerQueueCode not in licenseServerQueueCodes:
                continue
            
            # only running jobs
            if '@' in line:                
                hostInfo = parts[-1].strip()
                hostInfoParts = hostInfo.split('@')
                userName = hostInfoParts[0]
                host = hostInfoParts[-1]
                hostParts = host.split('=')
                noOfTokens = int(hostParts[-1])
                hostName = hostParts[0] + '.cax.lan'
                licenseServer = licenseServerQueueCodes[licenseServerQueueCode]
                
#                 if hostName in cls._hostsStat:
                jobId = len(outOfQueueJobsParams)
                attributes = {
                    'JB_job_number' : jobId,
                    'JB_name' : RunningJob.OUT_OF_THE_QUEUE_NAME,
                    'JB_owner' : userName,
                    'state' : 'r',
                    'JB_submission_time' : '-',
                    'queue_name': licenseServer.CODE + '@' + hostName,
                    'JAT_prio' : '-',
                    'full_job_name': 'N/A',
                    'hard_request' : noOfTokens,
                    'hard_req_queue' : licenseServer.CODE + '@*',
                    'JAT_start_time' : '-',
                    'slots' : '-'}
                
                outOfQueueJobsParams.append(attributes)
        
        return outOfQueueJobsParams
    
    #-------------------------------------------------------------------------
    @classmethod
    def _setupExecutionServers(cls):
        
        cls._hostsStat = xmlio.GridEngineInterface.getHostsStat()
                
        for hostName in cls._hostsStat:
            hostNameString = '@' + hostName
            executionServer = None
            
            try:
                executionServer = bi.BaseExecutionServerType.getServerFromName(hostNameString)
                cls.executionServers[hostName] = executionServer
            except bi.DataSelectorException as e:
                print str(e)
                
            
#             for serverType in EXECUTION_SERVER_TYPES.values():
#                 matchServer = re.match(serverType.PATTERN, hostNameString)
#                 if matchServer:
#                     executionServer = serverType(matchServer.group(1), hostNameString)
#                     break
#             
#             if executionServer is not None:
#                 cls.executionServers[hostName] = executionServer
#             else:
#                 raise DataSelectorException('Server name not recognised! name=%s' % hostName)
        
    #--------------------------------------------------------------------------
    @classmethod
    def getHostStat(cls, hostName):
                
        if hostName not in cls._hostsStat:
            raise xmlio.GridEngineInterfaceException('Unknown host name: %s' % hostName)
        
        return cls._hostsStat[hostName]
    
    #--------------------------------------------------------------------------
    @classmethod
    def _setAvailableHosts(cls):
            
        for licenceServer in bi.LICENSE_SERVER_TYPES:
            hosts = xmlio.GridEngineInterface.getAvailableHost(licenceServer.CODE)
            
            executionServers = list()
            for hostName in hosts:
                if hostName not in cls.executionServers:
                    print 'Host name not recognised! "%s"' % hostName
                    continue
                
                executionServer = cls.executionServers[hostName]
                executionServers.append(executionServer)
                
#                 # sort host according to their type
#                 if type(executionServer) is WorkstationExecutionServerType:
#                     executionServers.append(executionServer)
#                 else:
#                     executionServers.insert(0, executionServer)
            cls.availableLicenseServerHosts[licenceServer] = executionServers

    #--------------------------------------------------------------------------
    @classmethod
    def _setupJobsInQueue(cls):
        
        jobAttributes = xmlio.GridEngineInterface.getQueueStat()
        allLicenseTakingJobs = cls._getOutOfQueueJobsStat()
#         jobAttributes.extend(cls._getOutOfQueueJobsStat())
        
        # always clear content
        cls.jobsInQueue.clear()
        uniqueJobTags = list()
        for jobAttribute in jobAttributes: 
            job = RunningJob(jobAttribute)
            
            # check duplicate jobs
            jobTag = job['JB_owner']+job['state']+str(job['queue_name'])+str(job['hard_request'])
            
#             if jobTag not in uniqueJobTags:
            cls.jobsInQueue[job.id] = job
            uniqueJobTags.append(jobTag)
        
        for jobAttribute in allLicenseTakingJobs: 
            job = RunningJob(jobAttribute)
            
            # check duplicate jobs
            jobTag = job['JB_owner']+job['state']+str(job['queue_name'])+str(job['hard_request'])
            
            if jobTag not in uniqueJobTags:
                cls.jobsInQueue[job.id] = job
                uniqueJobTags.append(jobTag)
    
    #--------------------------------------------------------------------------
    @classmethod
    def _getTokenStatus(cls):
        
        stdout, _ = utils.runSubprocess(cls.QLIC_COMMAND)
        
        licenseServerTypes = list()
        licenseServerTypes.extend(bi.LICENSE_SERVER_TYPES)
        licenseServerTypes.extend(bi.PAMCRASH_LICENSE_SERVER_TYPES)
        licenseServerTypes.extend(bi.NASTRAN_LICENSE_SERVER_TYPES)
        
        lines = stdout.splitlines()
        
        for licenseServerType in licenseServerTypes:
            # locate corresponding line
            for line in lines:
                if licenseServerType.QUEUE_CODE in line:
                    break
                
            status = dict()
            for label, value in zip(cls.QLIC_COUMNS, line.split()):
                if label != 'resource':
                    try:
                        value = int(value)
                    except ValueError as e:
                        value = 0
                status[label] = value
            
            cls.tokenStatus[licenseServerType] = status
    
    #--------------------------------------------------------------------------
#     @classmethod
#     def getFileContent(cls, jobItem):
#         
#         tempFileObject = tempfile.NamedTemporaryFile()
#         tempFileName = tempFileObject.name
#         
#         utils.runSubprocess(command)
#         'rsync -avzPh --append-verify siegl@mb-so2:/scr1/scratch/grid/kmatejka/SK2160INK_A_FB_PV_front_bumper_001-08.5727/abaqus_v6.env /data/fem/users/siegl/eclipse/qaba/res/test_files/remote_test'
  
                        
#==============================================================================

class RunningJob(object):
    
    COLUMNS_WIDTHS = [6, 10, 12, 55, 4, 21, 25, 7, 6]
    OUT_OF_THE_QUEUE_NAME = 'Out of the queue'
    
    def __init__(self, attributes):
                
        self._attributes = attributes
                
        self.id = self._attributes['JB_job_number']
        self.name = self._attributes['JB_name']
        
        self.licenceServer = bi.BaseLicenseServerType.getLicenseServerTypeFromName(
            self._attributes['hard_req_queue'])
        
        self.noOfTokens = int(self._attributes['hard_request'])
        self.noOfCpus = self.licenceServer.getNoOfCpus(self.noOfTokens)
        
        self.isOutOfTheQueue = False
        if self.name == self.OUT_OF_THE_QUEUE_NAME:
            self.isOutOfTheQueue = True
                
        self.scratchPath = os.path.join(JobExecutionSetting.SCRATCH_PATH,
            self._attributes['JB_owner'], '%s.%s' % (self.name, self.id))
        
        self._idetifySolver()
        self._setDetailedAttributes()
                            
    #--------------------------------------------------------------------------
    
    def _setDetailedAttributes(self):
        
        if self.isOutOfTheQueue:
            return
        
        stdout, _ = utils.runSubprocess('qstat -j %s' % self.id)
        
        for line in stdout.splitlines()[1:]:
            parts = line.split(':')
            self._attributes[parts[0]] = ', '.join([p.strip() for p in parts[1:]])
        
    #--------------------------------------------------------------------------
    
    def _idetifySolver(self):
        
        self.solverType = bi.BaseSolverType.getSolverTypeFromName(
            self._attributes['hard_req_queue'])
                
    #--------------------------------------------------------------------------
    
    def __getitem__(self, attributeName):
        
        if attributeName in self._attributes:
            return self._attributes[attributeName]
        else:
            return None
    
    #--------------------------------------------------------------------------
    
    def getTooltip(self):
        
        attrNames = ['job_name','sge_o_workdir', 'owner','sge_o_host','mail_list']
        
        tooltip = '%s job' % self.solverType.NAME
        tooltip += '\nLicense = %s' % self.licenceServer.NAME        
        for attrName in attrNames:
            if attrName in self._attributes:
                tooltip += '\n%s = %s' % (attrName, self._attributes[attrName])
         
        return tooltip 
    
    #--------------------------------------------------------------------------
    
    def getInfo(self):
                
        return '\n'.join(['%s = %s' % (k, v) for k, v in self._attributes.iteritems()])
    
    #--------------------------------------------------------------------------
    
    def toString(self, colour=True):
        
        lineFormat = ['{:>%s}' % w for w in self.COLUMNS_WIDTHS]
        
        string = ''
        jobtime='not set'
        if self._attributes['state'] == 'r':
            jobtime = self._attributes['JAT_start_time']
        elif self._attributes['state'] == 'dt':
            jobtime = self._attributes['JAT_start_time']
        elif 'JB_submission_time' in self._attributes:
            jobtime = self._attributes['JB_submission_time']
        
        queueName = self._attributes['queue_name']
        if queueName is None:
            queueName = ''
        
        string += ''.join(lineFormat).format(
            self._attributes['JB_job_number'], self._attributes['JAT_prio'],
            self._attributes['JB_owner'], self.name,
            self._attributes['state'], jobtime, queueName,
            self._attributes['hard_request'], self._attributes['slots'])
        
#         if self.executionServer is not None:
#             print self.executionServer.freeCpuNo
        
        if self.isOutOfTheQueue and colour:
            string = utils.ConsoleColors.FAIL + string + utils.ConsoleColors.ENDC
        elif self.solverType is not None and colour:
            string = self.solverType.QUEUE_COLOUR + string + utils.ConsoleColors.ENDC
                
        return '\n'+ string
    
    #--------------------------------------------------------------------------
    
    def terminate(self):
        
        logging.debug('Terminating job: %s' % self.id)
        
        stdout, _ = utils.runSubprocess('qdel %s' % self.id)
        return stdout
    
    #--------------------------------------------------------------------------
    
#     def showContent(self):
#          
# #         scratchPath = os.path.join(JobExecutionSetting.SCRATCH_PATH,
# #             self._attributes['JB_owner'], '%s.%s' % (self.name, self.id))
# #         
# #         hostFullName = self._attributes['queue_name'].split('@')[-1]
# #         hostName = hostFullName.split('.')[0] 
# #         
# # #         ssh = subprocess.Popen(['ssh', '%s' % hostName, 'cd', scratchPath, 'ls'],
# #         ssh = subprocess.Popen(['ssh', '%s' % hostName],
# #             stdin=subprocess.PIPE,
# #             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
# #             universal_newlines=True,bufsize=0)
# #         
# # # #         stdout, _ = utils.runSubprocess('ssh -X %s; cd %s; ll, exit 0' % (hostName, scratchPath))
# # # #         ssh.stdin.write('cd %s\n' % scratchPath)
# # # #         ssh.stdin.write('ll\n')
# # # #         ssh.stdin.close()
# # #        
# #         
# #         
# #         ssh.stdin.write('cd %s\n' % scratchPath)
# #         ssh.stdin.write('ls .\n')
# #         ssh.stdin.close()
# #         
# #         stdout = ssh.stdout.readlines()
# #         stdout.extend(ssh.stderr.readlines())
# #         print hostName
# #         print scratchPath
# #         
# #         print stdout
#             
#         print self.getListOfFiles()
#         
# #         'rsync -avzPh --append-verify siegl@mb-so2:/scr1/scratch/grid/kmatejka/SK2160INK_A_FB_PV_front_bumper_001-08.5727/abaqus_v6.env /data/fem/users/siegl/eclipse/qaba/res/test_files/remote_test'
# #         
# #         self.runSubprocess('rsync -avzPh --append-verify %s:%s %s' % (
# #             'bmw_data_importer', scrPath, destPath))

    #--------------------------------------------------------------------------
    
    def getListOfFiles(self):
        
        hostFullName = self._attributes['queue_name'].split('@')[-1]
        hostName = hostFullName.split('.')[0] 
        
        ssh = subprocess.Popen(['ssh', '%s' % hostName],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True,bufsize=0)
                
        ssh.stdin.write('cd %s\n' % self.scratchPath)
        ssh.stdin.write('ls .\n')
        ssh.stdin.close()
        
        stdout = ssh.stdout.readlines()
#         stdout.extend(ssh.stderr.readlines())
        
        # check that output is a file
        fileList = list()
        for line in stdout:
            line = line.strip()
            if len(os.path.splitext(line)[-1]) > 2:
                fileList.append(line)
        
        return fileList
    
    #--------------------------------------------------------------------------
    
    def getTrackedFileContent(self, fileName):
        
        hostFullName = self._attributes['queue_name'].split('@')[-1]
        hostName = hostFullName.split('.')[0] 
        
        ssh = subprocess.Popen(['ssh', '%s' % hostName],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True,bufsize=0)
        
        path = os.path.join(self.scratchPath, str(fileName))
        
#         ssh.stdin.write('cat %s' % path)
        ssh.stdin.write('tail -n 100 %s' % path)
        ssh.stdin.close()

        return ssh.stdout.read()
        
        
#==============================================================================

class Queue(object):
    
    COLUMN_LABELS = ["JOB-ID","priority","user","job-name","st",
        "submit/start_at","queue name",'tokens', "slots"]
    
    resources = None
    
    def __init__(self):
        
        self.jobs = list()
        
        self.updateState()

    #-------------------------------------------------------------------------
    @classmethod
    def connectResources(cls, resources):
        cls.resources = resources
        
    #--------------------------------------------------------------------------
    
    def updateState(self):
        
        self.jobs = list()
        
        for job in self.resources.jobsInQueue.values():
            if job['state'] == 'r':
                self.jobs.insert(0, job)
            else:
                self.jobs.append(job)
        
#         self.jobs = self.resources.jobsInQueue
        
#         jobAttributes = xmlio.GridEngineInterface.getQueueStat()
#         
#         self.jobs = list()
#         for jobAttribute in jobAttributes: 
#             self.jobs.append(RunningJob(jobAttribute))
            
    #--------------------------------------------------------------------------
    
    def getColumnLabels(self):
        
        string = ''
        lineFormat = ['{:>%s}' % w for w in RunningJob.COLUMNS_WIDTHS]
        string += ''.join(lineFormat).format(*self.COLUMN_LABELS)
                
        return string
    
    #--------------------------------------------------------------------------
    
    def __repr__(self):
        
        self.updateState()
        
        string = self.getColumnLabels()
        string += '\n'+ 150*'-'
        
        for job in self.jobs:
            string += job.toString()
        
        return string
    
    