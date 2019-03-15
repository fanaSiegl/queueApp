#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Python script for '''

import os
import sys
import time
import copy

import utils
import base_items as bi
import enum_items as ei
from persistent import file_items as fi

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
                
    #--------------------------------------------------------------------------
    
    def setDescription(self, text):
        
        if len(text) > 15:
            text = text[:15]
        
        self.description = text
        
        print '\tJob description set to: %s' % self.description
        
    #--------------------------------------------------------------------------
    
    def setStartTime(self, startTime):
        
        self.startTime = startTime
        
        print '\tJob start time set to: %s' % self.startTime
    
    #--------------------------------------------------------------------------
    
    def setNumberOfCores(self, numberOfCores):
        
        self.numberOfCores = numberOfCores
        
        print '\tNumber of CPU set to: %s' % self.numberOfCores
    
    #--------------------------------------------------------------------------
    
    def setNumberOfGPUCores(self, numberOfGPUCores):
        
        self.numberOfGPUCores = numberOfGPUCores
        
        print '\tSelected GPGPU acceleration: %s' % self.numberOfGPUCores
    
    #--------------------------------------------------------------------------
    
    def setPriority(self, priority):
                
        print '\tJob priority set to: %s (-> %s)' % (priority, priority - 100)
        
        self.priority = priority - 100
    
    #--------------------------------------------------------------------------
    
    def setSolverVersion(self, solverVersion):
        
        self.solverVersion = solverVersion
        
        print '\tSelected version: %s' % self.solverVersion
            
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
        
        print '\tSelected license: %s' % self.licenseServer.NAME
    
    #--------------------------------------------------------------------------
    
    def setExecutionServer(self, executionServer):
        
        self.executionServer = executionServer
        
        print '\tSelected host: %s' % self.executionServer.name
    
    #--------------------------------------------------------------------------
    
    def setAdditionalSolverParams(self, params):
        
        if len(params) > 15:
            print 'Warning: not all parameters parsed! %s -> %s' % (params, params[:15])
            params = params[:15]
            
        self.additionalSolverParams = params
        
        print '\tAdditional solver parameters set to: %s' % self.additionalSolverParams
    
#==============================================================================

class BaseExecutionProfileType(object):

    container = ABAQUS_EXECUTION_PROFILE_TYPES

    def __init__(self, parentApplication):
        
        self.parentApplication = parentApplication
        self.job = AbaqusJob()
        self.jobSettings = JobExecutionSetting()
        self.user = bi.User()
        
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
        
        print "Info- Required licenses for this job are: %s" % self.job.getTokensRequired()
        
    #--------------------------------------------------------------------------

    def _setInputFile(self):
        
        inpSelector = bi.InputFileSelector(self.parentApplication)
        self.inpFileNames = inpSelector.getSelection()
        
        self.job.setInpFile(self.inpFileNames[0])
        
        print '\tSelected file(s): %s' % ', '.join([
            os.path.basename(inpFileName) for inpFileName in self.inpFileNames])
        
        # in case of restart read
        if self.job.inpFile.subAllFiles:
            inpSelector = bi.RestartInputFileSelector(self.parentApplication)
            restartInpFileName = inpSelector.getSelection()
            
            self.job.setRestartInpFile(restartInpFileName)
            
            print '\tSelected restart file: %s' % restartInpFileName
                    
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
        
        self.job.setSolverVersion(solverVersion)
        
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
            print "\tGPGPU acceleration is NOT AVAILABLE"
            return 0, 0, 0
        elif self.jobSettings.executionServer.NO_OF_GPU == 0:
            print "\tGPGPU acceleration is NOT AVAILABLE"
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
        
        freeLicenseServer = bi.BaseLicenseServerType.getFree()
        
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
            if host.freeCpuNo > defaultNoOfCores or defaultNoOfCores >= host.NO_OF_CORES:
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
    
    NAME = 'PamCrash analysis'
    ID = 0
        
    def __init__(self, parentApplication):
        
        self.parentApplication = parentApplication
        self.job = PamCrashJob()
        self.jobSettings = JobExecutionSetting()
        self.user = bi.User()
        
        self.inpFileNames = list()
        
    #--------------------------------------------------------------------------

    def _setInputFile(self):
        
        inpSelector = bi.PamcrashInputFileSelector(self.parentApplication)
        self.inpFileNames = inpSelector.getSelection()
        
        self.job.setInpFile(self.inpFileNames[0])
        
        print '\tSelected file(s): %s' % ', '.join([
            os.path.basename(inpFileName) for inpFileName in self.inpFileNames])
        
    #--------------------------------------------------------------------------

    def _setLicenseServer(self):
        
        bi.BaseDataSelector.printSelectionTitle('Available license servers')
        
        licenseServer = bi.PamCrashLicenseServerType
        
        print licenseServer.toOptionLine()
       
        self.jobSettings.setLicenseServer(licenseServer)

    #--------------------------------------------------------------------------
    
    def _setSolverVersion(self):
        
        solverVersion = ei.PAMCRASH_SOLVER_LIST[0]
        
        self.job.setSolverVersion(solverVersion)
        
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
            print "\tGPGPU acceleration is NOT AVAILABLE"
            return 0, 0, 0
        elif self.jobSettings.executionServer.NO_OF_GPU == 0:
            print "\tGPGPU acceleration is NOT AVAILABLE"
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
    