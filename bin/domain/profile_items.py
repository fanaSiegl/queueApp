#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Python script for '''

import os
import sys
import logging

import utils
import base_items as bi
import enum_items as ei
import comp_items as ci
import selector_items as si
from persistent import file_items as fi

#==============================================================================

ABAQUS_EXECUTION_PROFILE_TYPES = list()
PAMCRASH_EXECUTION_PROFILE_TYPES = list()
NASTRAN_EXECUTION_PROFILE_TYPES = list()
TOSCA_EXECUTION_PROFILE_TYPES = list()

#==============================================================================

class BaseExecutionProfileType(object):

    container = ABAQUS_EXECUTION_PROFILE_TYPES
    SOLVER_TYPE = bi.AbaqusSolverType
    
    DFT_POSTPROCESSING_OPTION_INDEX = 1
    
    def __init__(self, parentApplication):
        
        self.parentApplication = parentApplication
        self.job = ci.AbaqusJob()
        self.jobSettings = ci.JobExecutionSetting()
        self.user = ci.User()
        self.postProcessingType = bi.BasePostProcessingType(self.job)
        
        self.inpFileNames = list()
    
    #--------------------------------------------------------------------------
    
    def getCopy(self, profileType):
        
        ''' Returns a new type of profile with the current profile settings.  '''
                
        profile = profileType(self.parentApplication)
        profile.job = self.job
        profile.jobSettings = self.jobSettings
        profile.inpFileNames = self.inpFileNames
        profile.postProcessingType = self.postProcessingType   
         
        return profile
    
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
        self._setPostProcessingType()
        
        logging.info("Info- Required licenses for this job: %s" % self.job.getTokensRequired())
        
    #--------------------------------------------------------------------------

    def _setInputFile(self, inpFileNames=None):
        
        # switch between parametric and interactive input
        if inpFileNames is not None:
            self.inpFileNames = inpFileNames
        else:
            inpSelector = si.InputFileSelector(self.parentApplication)
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
            raise si.DataSelectorException('Use GUI version to handle restart simulation option.')
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
        
        licenseSelector = si.LicenseServerSelector(self.parentApplication)
        licenseSelector.DFT_OPTION_INDEX = self.getDftLicenseServerOption()
        licenseServer = licenseSelector.getSelection()
    
        self.jobSettings.setLicenseServer(licenseServer)
        
    #--------------------------------------------------------------------------
    
    def _setSolverVersion(self):
        
        solverVersionSelector = si.SolverVersionSelector(self.parentApplication)
        solverVersion = solverVersionSelector.getSelection()
        solverVersionPath = solverVersionSelector.VERSIONS.getSolverPath(solverVersion) 
        
        self.job.setSolverVersion(solverVersionPath)
        
    #--------------------------------------------------------------------------
    
    def _setExecutionServer(self):
        
        hostSelector = si.ExecutionServerSelector(self.parentApplication)
        hostSelector.DFT_OPTION_INDEX = self.getDftExectionServerOption()
        executionServer = hostSelector.getSelection()
        
        self.jobSettings.setExecutionServer(executionServer)
        
    #--------------------------------------------------------------------------
    
    def _setJobDescription(self):
        
        si.BaseDataSelector.printSelectionTitle('Job description')
        
        jobDescription = si.BaseDataSelector.getTextInput(
            'Enter description of job [15 characters, enter="-"]: ', '-')
                
        self.job.setDescription(jobDescription)
    
    #--------------------------------------------------------------------------
    
    def _setJobStartTime(self):
        
        si.BaseDataSelector.printSelectionTitle('Job start time')
        
        jobStartTime = si.BaseDataSelector.getTimeInput(
            'Enter deferred time of computation [MMDDhhmm, enter=put ASAP into queue]: ',
            self.job.startTime)
        
        self.job.setStartTime(jobStartTime)
            
    #--------------------------------------------------------------------------
    
    def _setNumberOfCores(self):
        
        minValue, maxValue, dftValue = self.getDftNoOfCores()
        
        numberOfCores = si.BaseDataSelector.getIntInput('Choose the number of CPU', 
            'Enter number of CPU cores [max %s, enter=%s]: ' % (
                maxValue, dftValue),
            minValue, maxValue, dftValue)
        
        self.job.setNumberOfCores(numberOfCores)
    
    #--------------------------------------------------------------------------
    
    def _setNumberOfGPUCores(self):        
                
        minValue, maxValue, dftValue = self.getDftNoOfGpus()
        
        if maxValue > 0:
            numberOfGPUCores = si.BaseDataSelector.getIntInput('Choose the number of GPU', 
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
        
        priority = si.BaseDataSelector.getIntInput('Choose job priority', 
            'Enter priority in the queue [%s-%s, enter=%s]: ' % (
                minValue, maxValue, dftValue),
            minValue=minValue, maxValue=maxValue, dftValue=dftValue)
          
        self.job.setPriority(priority)
    
    #--------------------------------------------------------------------------
    
    def _setAdditionalSolverParams(self):
        
        si.BaseDataSelector.printSelectionTitle('Additional parameters for solver')
        
        params = si.BaseDataSelector.getTextInput(
            'Specify more job parameters [15 characters, enter="%s"]: ' % self.getDftAdditionalSolverParams(),
            self.getDftAdditionalSolverParams())
        
        self.jobSettings.setAdditionalSolverParams(params)
    
    #--------------------------------------------------------------------------
    
    def _setPostProcessingType(self):
        
        selector = si.PostProcessingSelector(self.parentApplication)
        selector.DFT_OPTION_INDEX = self.DFT_POSTPROCESSING_OPTION_INDEX
        postProcessingType = selector.getSelection()
        
        self.postProcessingType = postProcessingType(self.job)
        
    #--------------------------------------------------------------------------
    
    def getDftAdditionalSolverParams(self):
        
        return ''

    #--------------------------------------------------------------------------

    def getDftLicenseServerOption(self):
                
        return si.LicenseServerSelector.DFT_OPTION_INDEX

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
        
        return si.ExecutionServerSelector.DFT_OPTION_INDEX
    
    #--------------------------------------------------------------------------
    
    def getDftJobPriority(self):
        
        return 40, 60, self.job.DFT_PRIORITY
    
    #--------------------------------------------------------------------------
    
    def getDftPostProcessingOption(self):
        
        return self.DFT_POSTPROCESSING_OPTION_INDEX
        
#==============================================================================
@utils.registerClass
class DatacheckExecutionProfileType(BaseExecutionProfileType):
    
    NAME = 'Datacheck - start immediately (1 CPU on local workstation)'
    ID = 5
    
    DATACHECK_CPU_NO = 1
    DATACHECK_TOKEN_NO = 30
    DFT_LICENSE_TYPE = bi.Var2LicenseServerType
            
#     #--------------------------------------------------------------------------
#      
#     def _setLicenseServer(self):
#          
#         self.job.setNumberOfCores(self.DATACHECK_CPU_NO)
#         self.job.fixTokenNumber = self.DATACHECK_TOKEN_NO
# 
# #TODO: fix token number for datacheck
# #         tokensRequired = bi.DslsLicenseType.getNoOfTokens(self.job.numberOfCores)
#         tokensRequired = self.DATACHECK_TOKEN_NO
#         licenseServer = bi.BaseLicenseServerType.getFreeFromTokens(tokensRequired)
#         
#         self.jobSettings.setLicenseServer(licenseServer)
    
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
        
        self.job.setNumberOfCores(self.DATACHECK_CPU_NO)
        self.job.fixTokenNumber = self.DATACHECK_TOKEN_NO
        
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
                        
        return 1, self.DATACHECK_CPU_NO, self.DATACHECK_CPU_NO

    #--------------------------------------------------------------------------
    
    def getDftExectionServerOption(self):
        
        hostSelector = si.ExecutionServerSelector(self.parentApplication)
        hosts, infoLines, serverHosts, userHosts, description = hostSelector.getOptions()
        
        # check available AP host
        for host in userHosts:    
            if host.isUserMachine:
                return hosts.index(host) + 1
        
        return 1
    
    #--------------------------------------------------------------------------

    def getDftLicenseServerOption(self):
                
        return bi.LICENSE_SERVER_TYPES.index(self.DFT_LICENSE_TYPE) + 1
        
    
#==============================================================================
@utils.registerClass
class LicensePriorityExecutionProfileType(BaseExecutionProfileType):
    
    NAME = 'License priority - use any free license (reduce CPU and start on any free server)'
    ID = 4
    
    DFT_POSTPROCESSING_OPTION_INDEX = 2
    
    #--------------------------------------------------------------------------

    def _getPreferredNumberOfCpus(self):
        
        status = self.jobSettings.licenseServer.getTokenStatus()
        defaultNoOfCores = self.jobSettings.licenseServer.getNoOfCpus(int(status['free']))
        
        return defaultNoOfCores
    
    #--------------------------------------------------------------------------

    def getDftLicenseServerOption(self):
        
        freeLicenseServer = bi.BaseLicenseServerType.getFree(self.SOLVER_TYPE.NAME)
        if freeLicenseServer is None:
            return si.LicenseServerSelector.DFT_OPTION_INDEX
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
        
        hostSelector = si.ExecutionServerSelector(self.parentApplication)
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
class ResourcePriority1ExecutionProfileType(BaseExecutionProfileType):
    
    NAME = 'Resource priority 1 - use preferred license, CPU and server'
    ID = 1
    
    DFT_LICENSE_TYPE = bi.CommercialLicenseServerType
    DFT_NO_OF_CORES = 32
    DFT_EXECUTION_SERVER_INDEX = 3
    DFT_POSTPROCESSING_OPTION_INDEX = 2
    
    #--------------------------------------------------------------------------

    def getDftLicenseServerOption(self):
                
        return bi.LICENSE_SERVER_TYPES.index(self.DFT_LICENSE_TYPE) + 1

    #--------------------------------------------------------------------------

    def getDftNoOfCores(self):   
    
        maxValue = self.jobSettings.executionServer.NO_OF_CORES
        minValue = 1
        dftValue = self.DFT_NO_OF_CORES
        
        return minValue, maxValue, dftValue
    
    #--------------------------------------------------------------------------
    
    def getDftExectionServerOption(self):
        
        return self.DFT_EXECUTION_SERVER_INDEX
    
    #--------------------------------------------------------------------------
    
    def getDftAdditionalSolverParams(self):
        
        params = ''
        # check v2019 version
        if self.job.solverVersion == ei.AbaqusSolverVersions.getSolverPath('abaqus2019x'):
            params = 'threads=4'

        return params
    

#==============================================================================
@utils.registerClass
class ResourcePriority2ExecutionProfileType(ResourcePriority1ExecutionProfileType):
    
    NAME = 'Resource priority 2 - use preferred license, CPU and server'
    ID = 2
    DFT_LICENSE_TYPE = bi.Var1LicenseServerType
    DFT_NO_OF_CORES = 12
    DFT_EXECUTION_SERVER_INDEX = 2

#==============================================================================
@utils.registerClass
class ResourcePriority3ExecutionProfileType(ResourcePriority1ExecutionProfileType):
    
    NAME = 'Resource priority 3 - use preferred license, CPU and server'
    ID = 3
    DFT_LICENSE_TYPE = bi.Var2LicenseServerType
    DFT_NO_OF_CORES = 6
    DFT_EXECUTION_SERVER_INDEX = 1
    
    #--------------------------------------------------------------------------
    
    def getDftAdditionalSolverParams(self):
        
        return ''

#==============================================================================
@utils.registerClass
class AutoPriority1ExecutionProfileType(ResourcePriority3ExecutionProfileType):
    
    NAME = 'Auto - use preferred profile based on the current availability'
    ID = 0
    
    #--------------------------------------------------------------------------
    
    def __init__(self, parentApplication):
        
        super(AutoPriority1ExecutionProfileType, self).__init__(parentApplication)
        
        self.activeProfile = ResourcePriority3ExecutionProfileType
        self._findAvailableProfileSettings()
            
    #--------------------------------------------------------------------------
    
    def _findAvailableProfileSettings(self):
         
        freeLicenseServer = bi.BaseLicenseServerType.getFree(self.SOLVER_TYPE.NAME)
        serverHosts = freeLicenseServer.getAPservers()
        
        def _checkProfileAvailability(profile):
            
            # check available profiles
            noOfCoresProfile = profile.DFT_NO_OF_CORES
            noOfFreeCoresAtPreferedServerProfile = serverHosts[profile.DFT_EXECUTION_SERVER_INDEX - 1].freeCpuNo
            
            if (freeLicenseServer == profile.DFT_LICENSE_TYPE and 
                 noOfFreeCoresAtPreferedServerProfile >= noOfCoresProfile):

                return profile.DFT_LICENSE_TYPE, profile.DFT_NO_OF_CORES, profile.DFT_EXECUTION_SERVER_INDEX
            else:
                return None
        
        profiles = [
            ResourcePriority1ExecutionProfileType,
            ResourcePriority2ExecutionProfileType,
            ResourcePriority3ExecutionProfileType]
        
        for profile in profiles:
            settings = _checkProfileAvailability(profile)
            
            if settings is not None:
                self.DFT_LICENSE_TYPE = settings[0]
                self.DFT_NO_OF_CORES = settings[1]
                self.DFT_EXECUTION_SERVER_INDEX = settings[2]
                
                self.activeProfile = profile  
                break
        
        logging.debug('Auto profile setting set to: %s' % profile.NAME)
    
    #--------------------------------------------------------------------------
    
    def getDftAdditionalSolverParams(self):
        
        if self.activeProfile is not ResourcePriority3ExecutionProfileType:
            if self.job.solverVersion == ei.AbaqusSolverVersions.getSolverPath('abaqus2019x'):
                return 'threads=4'
            
        return '' 
        
#==============================================================================
@utils.registerClass
class PamCrashExecutionProfileType(BaseExecutionProfileType):
    
    container = PAMCRASH_EXECUTION_PROFILE_TYPES
    SOLVER_TYPE = bi.PamCrashSolverType
    
    NAME = 'PamCrash analysis'
    ID = 0
    
    DFT_POSTPROCESSING_OPTION_INDEX = 2
        
    def __init__(self, parentApplication):
        
        self.parentApplication = parentApplication
        self.job = ci.PamCrashJob()
        self.jobSettings = ci.JobExecutionSetting()
        self.user = ci.User()
        self.postProcessingType = bi.BasePostProcessingType(self.job)
        
        self.inpFileNames = list()
        
    #--------------------------------------------------------------------------

    def _setInputFile(self):
        
        inpSelector = si.PamcrashInputFileSelector(self.parentApplication)
        self.inpFileNames = inpSelector.getSelection()
        
        self.job.setInpFile(self.inpFileNames[0], self)
        
        logging.info('Selected file(s): %s' % ', '.join([
            os.path.basename(inpFileName) for inpFileName in self.inpFileNames]))
                
    #--------------------------------------------------------------------------

    def _setLicenseServer(self):
        
        si.BaseDataSelector.printSelectionTitle('Available license servers')
        
        licenseServer = bi.PamCrashLicenseServerType
        
        logging.info(licenseServer.toOptionLine())
       
        self.jobSettings.setLicenseServer(licenseServer)

    #--------------------------------------------------------------------------
    
    def _setSolverVersion(self):
        
#         solverVersion = ei.PAMCRASH_SOLVER_LIST[0]
        solverVersionSelector = si.PamCrashSolverVersionSelector(self.parentApplication)
        solverVersion = solverVersionSelector.getSelection()
        solverVersionPath = solverVersionSelector.VERSIONS.getSolverPath(solverVersion) 
        
        self.job.setSolverVersion(solverVersionPath)
        
    #--------------------------------------------------------------------------
    
    def _setExecutionServer(self):
        
        hostSelector = si.PamCrashExecutionServerSelector(self.parentApplication)
        executionServer = hostSelector.getSelection()
        
        self.jobSettings.setExecutionServer(executionServer)        
    
    #--------------------------------------------------------------------------
    
#     def _setPostProcessingType(self):
#         
#         pass
    
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
        
        return si.PamCrashExecutionServerSelector.DFT_OPTION_INDEX
    
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
    
    #--------------------------------------------------------------------------
    
    def _setPostProcessingType(self):
         
        pass
    
    #--------------------------------------------------------------------------
    
    def getDftNoOfCores(self):
                        
        return 1, self.DATACHECK_CPU_NO, self.DATACHECK_CPU_NO


#==============================================================================
@utils.registerClass
class NastranExecutionProfileType(BaseExecutionProfileType):
    
    container = NASTRAN_EXECUTION_PROFILE_TYPES
    SOLVER_TYPE = bi.NastranSolverType
    
    NAME = 'Nastran analysis'
    ID = 0
    
    DFT_NO_OF_CORES = 1
    DFT_EXECUTION_SERVER_INDEX = 1
    DFT_LICENSE_SERVER_INDEX = 1
        
    def __init__(self, parentApplication):
        
        self.parentApplication = parentApplication
        self.job = ci.NastranJob()
        self.jobSettings = ci.JobExecutionSetting()
        self.user = ci.User()
        self.postProcessingType = bi.BasePostProcessingType(self.job)
        
        self.inpFileNames = list()
    
    #--------------------------------------------------------------------------

    def _setInputFile(self):
        
        inpSelector = si.NastranInputFileSelector(self.parentApplication)
        self.inpFileNames = inpSelector.getSelection()
        
        self.job.setInpFile(self.inpFileNames[0])
        
        logging.info('Selected file(s): %s' % ', '.join([
            os.path.basename(inpFileName) for inpFileName in self.inpFileNames]))
        
    #--------------------------------------------------------------------------

    def _setLicenseServer(self):
        
        si.BaseDataSelector.printSelectionTitle('Available license servers')
        
        licenseServer = bi.NastranLicenseServerType
        
        logging.info(licenseServer.toOptionLine())
       
        self.jobSettings.setLicenseServer(licenseServer)

    #--------------------------------------------------------------------------
    
    def _setSolverVersion(self):
        
        solverVersionSelector = si.NastranSolverVersionSelector(self.parentApplication)
        solverVersion = solverVersionSelector.getSelection()
        solverVersionPath = solverVersionSelector.VERSIONS.getSolverPath(solverVersion) 
        
        self.job.setSolverVersion(solverVersionPath)
        
    #--------------------------------------------------------------------------
    
    def _setExecutionServer(self):
        
        hostSelector = si.NastranExecutionServerSelector(self.parentApplication)
        hostSelector.DFT_OPTION_INDEX = self.getDftExectionServerOption()
        executionServer = hostSelector.getSelection()
        
        self.jobSettings.setExecutionServer(executionServer)     

    #--------------------------------------------------------------------------
    
    def _setNumberOfCores(self):
                
        self.job.setNumberOfCores(self.DFT_NO_OF_CORES)
        
    #--------------------------------------------------------------------------
    
    def _setNumberOfGPUCores(self):        
                        
        self.job.setNumberOfGPUCores(0)
            
    #--------------------------------------------------------------------------

    def getDftLicenseServerOption(self):
                
        return self.DFT_LICENSE_SERVER_INDEX
    
    #--------------------------------------------------------------------------
    
    def getDftExectionServerOption(self):
        
        return self.DFT_EXECUTION_SERVER_INDEX
    
    #--------------------------------------------------------------------------

    def getDftNoOfCores(self):   
    
        maxValue = 1#self.jobSettings.executionServer.NO_OF_CORES
        minValue = 1
        
        return minValue, maxValue, self.DFT_NO_OF_CORES
    
    #--------------------------------------------------------------------------

    def getDftNoOfGpus(self):
                    
        return 0, 0, 0

#==============================================================================

@utils.registerClass
class ToscaExecutionProfileType(BaseExecutionProfileType):
    
    container = TOSCA_EXECUTION_PROFILE_TYPES
    SOLVER_TYPE = bi.ToscaSolverType
    
    NAME = 'Tosca analysis'
    ID = 0
    
    DFT_NO_OF_CORES = 4
    DFT_EXECUTION_SERVER_INDEX = 1
    DFT_LICENSE_SERVER_INDEX = 1
        
    def __init__(self, parentApplication):
        
        self.parentApplication = parentApplication
        self.job = ci.ToscaJob()
        self.jobSettings = ci.JobExecutionSetting()
        self.user = ci.User()
        self.postProcessingType = bi.BasePostProcessingType(self.job)
        
        self.inpFileNames = list()
            
    #--------------------------------------------------------------------------

    def _setInputFile(self):
        
        inpSelector = si.ToscaInputFileSelector(self.parentApplication)
        self.inpFileNames = inpSelector.getSelection()
        
        self.job.setInpFile(self.inpFileNames[0])
        
        logging.info('Selected file(s): %s' % ', '.join([
            os.path.basename(inpFileName) for inpFileName in self.inpFileNames]))
        
    #--------------------------------------------------------------------------
    
    def _setSolverVersion(self):
        
        solverVersionSelector = si.ToscaSolverVersionSelector(self.parentApplication)
        solverVersion = solverVersionSelector.getSelection()
        solverVersionPath = solverVersionSelector.VERSIONS.getSolverPath(solverVersion) 
        
        self.job.setToscaSolverVersion(solverVersionPath)
        
        # run ABAQUS selection
        super(ToscaExecutionProfileType, self)._setSolverVersion()  
        
    #--------------------------------------------------------------------------
    
    def _setNumberOfGPUCores(self):        
                        
        self.job.setNumberOfGPUCores(0)
            
    #--------------------------------------------------------------------------
    
    def _setPostProcessingType(self): pass
    
    #--------------------------------------------------------------------------

    def getDftLicenseServerOption(self):
    
        return self.DFT_LICENSE_SERVER_INDEX
    
    #--------------------------------------------------------------------------
    
    def getDftExectionServerOption(self):
        
        return self.DFT_EXECUTION_SERVER_INDEX
    
    #--------------------------------------------------------------------------

    def getDftNoOfCores(self):   
    
        maxValue = self.jobSettings.executionServer.NO_OF_CORES
        minValue = 1
        
        return minValue, maxValue, self.DFT_NO_OF_CORES
    
    #--------------------------------------------------------------------------

    def getDftNoOfGpus(self):
                    
        return 0, 0, 0

#==============================================================================

class AbaqusExecutionProfileSelector(si.BaseDataSelector):
    
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

class PamCrashExecutionProfileSelector(AbaqusExecutionProfileSelector):
    
    DFT_OPTION_INDEX = 1
    profiles = PAMCRASH_EXECUTION_PROFILE_TYPES

#==============================================================================

class NastranExecutionProfileSelector(AbaqusExecutionProfileSelector):
    
    DFT_OPTION_INDEX = 1
    profiles = NASTRAN_EXECUTION_PROFILE_TYPES

#==============================================================================

class ToscaExecutionProfileSelector(AbaqusExecutionProfileSelector):
    
    DFT_OPTION_INDEX = 1
    profiles = TOSCA_EXECUTION_PROFILE_TYPES


