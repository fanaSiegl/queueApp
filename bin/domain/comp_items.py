#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Python script for '''

import os
import sys
import time
import copy
import shutil
import subprocess
import thread
import logging
import tempfile
import glob

import utils
import base_items as bi
import enum_items as ei
import selector_items as si
import profile_items as pi
from persistent import file_items as fi
from interfaces import xmlio

#==============================================================================

class JobException(Exception): pass

#==============================================================================

class AbaqusJob(object):
    
    DFT_PRIORITY = 50
    EXECUTABLE_FILE_TYPE = fi.AbaqusJobExecutableFile
    INPUT_FILE_TYPE = fi.AbaqusInpFile
    SOLVER_TYPE = bi.AbaqusSolverType
    
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
    
    def _checkProfile(self, parentProfile): pass
    
    #--------------------------------------------------------------------------
    
    def setInpFile(self, inpFileName, parentProfile=None):
        
        self.inpFile = self.INPUT_FILE_TYPE(inpFileName)
        
        self._checkProfile(parentProfile)
            
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
    INPUT_FILE_TYPE = fi.PamCrashInpFile
    SOLVER_TYPE = bi.PamCrashSolverType
    
    #--------------------------------------------------------------------------
    
    def _checkProfile(self, parentProfile):
        
        logging.debug('Checking DATACHECK KEY WORD')
        
        # in case there was no input file specified
        if self.inpFile is None:
            return
        
        isDataCheck = self.inpFile.dataCheck
        if type(parentProfile) is pi.PamCrashDataCheckExecutionProfileType and not isDataCheck:
            logging.debug('profile: DATACHECK, KEY WORD: N/A - adding')
            self.inpFile.switchDataCheckMode()
        elif type(parentProfile) is pi.PamCrashDataCheckExecutionProfileType and isDataCheck:
            logging.debug('profile: DATACHECK, KEY WORD: PRESENT - OK')
        elif isDataCheck:
            logging.debug('profile: EXECUTION, KEY WORD: DATACHECK - removing')
            self.inpFile.switchDataCheckMode()
        else:
            logging.debug('profile: EXECUTION, KEY WORD: N/A - OK')
    
    #--------------------------------------------------------------------------
    
    def getTokensRequired(self):
        
        if self.fixTokenNumber is not None:
            return self.fixTokenNumber
        
        tokensRequired = 0
        
        # obtain number of tokens according to number of cores
        tokensRequired += bi.PamcrashLicenseType.getNoOfTokens(self.numberOfCores)
        
        return tokensRequired

#==============================================================================

class NastranJob(AbaqusJob):
      
    EXECUTABLE_FILE_TYPE = fi.NastranJobExecutableFile
    INPUT_FILE_TYPE = fi.NastranInpFile
    SOLVER_TYPE = bi.NastranSolverType
        
    #--------------------------------------------------------------------------
    
    def getTokensRequired(self):
        
        if self.fixTokenNumber is not None:
            return self.fixTokenNumber
        
        tokensRequired = 0
        
        # obtain number of tokens according to number of cores
        tokensRequired += bi.NastranLicenseType.getNoOfTokens(self.numberOfCores)
        
        return tokensRequired

#==============================================================================

class ToscaJob(AbaqusJob):
      
    EXECUTABLE_FILE_TYPE = fi.ToscaJobExecutableFile
    INPUT_FILE_TYPE = fi.ToscaInpFile
    SOLVER_TYPE = bi.ToscaSolverType
    
    def __init__(self):
        super(ToscaJob, self).__init__()
        
        self.numberOfSolverCores = 1
        self.toscaSolverVersion = ''
    
    #--------------------------------------------------------------------------
    
    def setSolverVersion(self, toscaSolverVersion):
        
        self.toscaSolverVersion = toscaSolverVersion
        
        logging.info('Selected TOSCA version: %s' % self.toscaSolverVersion)
    
    #--------------------------------------------------------------------------
    
    def getTokensRequired(self):
        
        # original number of tokens based of CPU number
        tokensRequired = bi.DslsLicenseType.getNoOfTokens(self.numberOfSolverCores)
        
        # search analysis type
        if len(self.inpFile.abaqusInputFiles) > 0:
            abaqusInputFile = self.inpFile.abaqusInputFiles[0]
            if abaqusInputFile.stepPerturbation:
                tokensRequired += 50
            else:
                tokensRequired += 80
        else:
            raise fi.ToscaInpFileException(
                'No ABAQUS input file found in TOSCA *.par file! ("%s")' % self.inpFile.fileName)
        
        return tokensRequired
    
    #--------------------------------------------------------------------------
    
    def setNumberOfSolverCores(self, numberOfCores):
        
        self.numberOfSolverCores = numberOfCores
        
        logging.info('Number of ABAQUS CPU set to: %s' % self.numberOfSolverCores)
               
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
        cls._setupAvailableMetaPostprocessing()
        
        cls._setupLicenseRestriction()
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
    
    #---------------------------------------------------------------------------
    @classmethod
    def _setupLicenseRestriction(cls):
        
        for licenseServerTypeName, restrictionSettings in utils.getRestrictionConfig().iteritems():
            
            restriction = bi.BaseLicenseRestrictionType.getFromConfig(
                licenseServerTypeName, restrictionSettings)
                        
            licenseServerType = bi.BaseLicenseServerType.getLicenseServerTypeFromName(licenseServerTypeName)
            licenseServerType.setRestriction(restriction)
        
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
            except si.DataSelectorException as e:
                logging.error(str(e))
                
            
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
        
        outOfTheQueueTags = dict()
        hasJustFinishedTags = list()
        
        # check finished jobs
        currentJobIds = [jobAttribute['JB_job_number'] for jobAttribute in jobAttributes]
        
        for job in cls.jobsInQueue.values():
            if job.id not in currentJobIds and not job.isOutOfTheQueue:
                job.setHasFinished(True)
                cls.jobsInQueue.pop(job.id)
                hasJustFinishedTags.append(job.jobTag)
                
            # gather all existing out-of-the queue jobs
            if job.isOutOfTheQueue:
                outOfTheQueueTags[job.jobTag] = job
        
        # check job states
        uniqueJobTags = list()
        for jobAttribute in jobAttributes:
            
            currentJobId = jobAttribute['JB_job_number']
            jobTag = RunningJob.getTag(jobAttribute)
            
            # update already existing job in the queue
            if currentJobId in cls.jobsInQueue:
                cls.jobsInQueue[currentJobId].updateAttributes(jobAttribute)
                
            # add a new job
            else:
                try:
                    job = RunningJob(jobAttribute)
                    cls.jobsInQueue[job.id] = job
                except bi.LicenseServerException as e:
                    logging.debug(e)
                    continue
                                            
            uniqueJobTags.append(jobTag)
        
        currentOutOfTheQueueTags = list()
        for jobAttribute in allLicenseTakingJobs: 
            
            jobTag = RunningJob.getTag(jobAttribute)
            
            # add a new out-of-the-queue job
            if jobTag not in uniqueJobTags and jobTag not in outOfTheQueueTags.keys():
                try:
                    job = RunningJob(jobAttribute)
                    cls.jobsInQueue[job.id] = job
                    currentOutOfTheQueueTags.append(job.jobTag)
                except bi.LicenseServerException as e:
                    logging.debug(e)
                    continue
            # still running out-of-the-queue job
            elif jobTag not in uniqueJobTags and jobTag in outOfTheQueueTags.keys():
                currentOutOfTheQueueTags.append(jobTag)
        
        # check if out-of-the-queue job has finished
        # maybe there is a better way how to check local running jobs?
        # job will be removed in the next update...
        for job in outOfTheQueueTags.values():
            if job.jobTag not in currentOutOfTheQueueTags:
                job.setHasFinished(True)
        
    #--------------------------------------------------------------------------
    @classmethod
    def _getTokenStatus(cls):
        
        stdout, _ = utils.runSubprocess(cls.QLIC_COMMAND)
        
        licenseServerTypes = list()
        licenseServerTypes.extend(bi.LICENSE_SERVER_TYPES)
#         licenseServerTypes.extend(bi.PAMCRASH_LICENSE_SERVER_TYPES)
#         licenseServerTypes.extend(bi.NASTRAN_LICENSE_SERVER_TYPES)
        
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
    @classmethod
    def _setupAvailableMetaPostprocessing(cls):
        
        for path in os.listdir(ei.META_POST_PROCESSING_PATH):
            fullPath = os.path.join(ei.META_POST_PROCESSING_PATH, path)
            if not os.path.isdir(fullPath):
                continue
            for solverTypeName, solverType in bi.SOLVER_TYPES.iteritems():
                if solverTypeName.upper() in path.upper():                    
                    sessionFileList = glob.glob(os.path.join(fullPath, '*.ses'))
                    if len(sessionFileList) == 1:
                        sessionFilePath = sessionFileList[0]
                        
                        newClass = type('%s_MetaPostProcessingType' % path,
                            (bi.BaseMetaPostProcessingType, ), {
                                'metaSessionPath' : sessionFilePath,
                                'NAME' : path})
                        
                        solverType.registerPostProcessingType(newClass)
                            
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
    
    COLUMNS_WIDTHS = [6, 10, 12, 55, 4, 21, 26, 7, 6]
    OUT_OF_THE_QUEUE_NAME = 'Out of the queue'
    
    ATTRIBUTE_NAMES = [
        'exec_file', 'JAT_prio', 'binding', 'JB_job_number','notify', 
        'sge_o_log_name', 'owner', 'mail_list', 'JAT_start_time', 'job_number', 
        'uid', 'sge_o_shell', 'sge_o_home', 'group', 'sge_o_workdir', 'queue_name', 
        'priority', 'state', 'gid', 'binding       1', 'hard_req_queue', 'slots', 
        'cwd', 'mail_options', 'context', 'jobshare', 'soft_req_queue', 
        'execution_time', 'job_type', 'hard_queue_list', 'JB_owner', 
        'scheduling info', 'hard resource_list', 'submission_time', 
        'soft_queue_list', 'usage         1', 'script_file', 'env_list', 
        'account', 'sge_o_path', 'hard_request', 'job_name', 'sge_o_host', 
        'merge', 'full_job_name', 'JB_name', 'queue_name_hr']
    
    def __init__(self, attributes):
                
        self._attributes = attributes
        
        self.id = self._attributes['JB_job_number']
        self.name = self._attributes['JB_name']
        self.jobTag = self.getTag(attributes)
        
        self.licenceServer = bi.BaseLicenseServerType.getLicenseServerTypeFromCode(
            self._attributes['hard_req_queue'])
        
        noOfTokens = 0
        for key in self._attributes:
            if 'hard_request' in key:
                try:
                    noOfTokens = int(self._attributes['hard_request'])
                    break
                except Exception:
                    continue
        
        self.noOfTokens = noOfTokens#int(self._attributes['hard_request'])
        self.noOfCpus = self.licenceServer.getNoOfCpus(self.noOfTokens)
        
        self.treeItem = None
        self.hasFinished = False
        self.isOutOfTheQueue = False
        if self.name == self.OUT_OF_THE_QUEUE_NAME:
            self.isOutOfTheQueue = True
                            
        self.scratchPath = os.path.join(JobExecutionSetting.SCRATCH_PATH,
            self._attributes['JB_owner'], '%s.%s' % (self.name, self.id))
        
        self._idetifySolver()
        self._setDetailedAttributes()
                    
    #--------------------------------------------------------------------------
    
    @staticmethod
    def getTag(attributes):
        
        return attributes['JB_owner']+attributes['state']+str(attributes['queue_name'])+str(attributes['hard_request'])
    
    #--------------------------------------------------------------------------
    
    def setTreeItem(self, treeItem):
        
        self.treeItem = treeItem
        
    #--------------------------------------------------------------------------
    
    def setHasFinished(self, state):
        
        self.hasFinished = state
        
        if self.hasFinished and self.treeItem is not None:
            self.treeItem.parentJobFinished()
         
    #--------------------------------------------------------------------------
    
    def _setDetailedAttributes(self):
        
        # prevent None in queue_name
        queueName = self._attributes['queue_name']
        if queueName is None and 'soft_req_queue' in self._attributes:
            self._attributes['queue_name'] = self._attributes['soft_req_queue']
        elif queueName is None:
            self._attributes['queue_name'] = self._attributes['hard_req_queue']
            
            # try to replace missing host
            if '*' in self._attributes['hard_req_queue']:
                for key, value in self._attributes.iteritems():
                    if 'hard_request' in key and '.lan' in value:
                        self._attributes['queue_name'] = self._attributes['hard_req_queue'].replace(
                            '*', value)
                        break                
            
        self._attributes['queue_name_hr'] = '%s@%s' % (
            self.licenceServer.NAME, self._attributes['queue_name'].split('@')[-1])
        
        if self.isOutOfTheQueue:
            return
        
        stdout, _ = utils.runSubprocess('qstat -j %s' % self.id)
        
        lines = stdout.splitlines()
        for line in lines[1:]:
            parts = line.split(':')
            self._attributes[parts[0]] = ', '.join([p.strip() for p in parts[1:]])
                    
        self._attributes['priority'] = self._attributes['JAT_prio']
                
        # update tree item attributes when all attributes are obtained
        if self.treeItem is not None:
            self.treeItem.updateAttributes()
                    
    #--------------------------------------------------------------------------
    
    def updateAttributes(self, attributes):
        
        self._attributes = attributes
        
        thread.start_new_thread(self._setDetailedAttributes, ())
    
    #--------------------------------------------------------------------------
    
    def _idetifySolver(self):
        
        self.solverType = bi.BaseSolverType.getSolverTypeFromName(
            self._attributes['hard_req_queue'])
                
    #--------------------------------------------------------------------------
    
    def __getitem__(self, attributeName):
        
        if attributeName in self._attributes:
            return self._attributes[attributeName]
        else:
            return ''
    
    #--------------------------------------------------------------------------
    
    def getListOfAttributes(self):
        
        return sorted(self.ATTRIBUTE_NAMES)
    
    #--------------------------------------------------------------------------
    
    def getAttribute(self, attributeName):
        
        if attributeName in self._attributes:
            value = self._attributes[attributeName]
            if value is None:
                return '' 
            else:
                return value
        else:
            return ''
        
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
        
        # this should never happen
        if 'queue_name_hr' in self._attributes:
            queueName = self._attributes['queue_name_hr']
        else:
            queueName = self._attributes['queue_name']
#         if queueName is None:
#             queueName = self._attributes['soft_req_queue']
        
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
        
        if self._attributes['state'] == 'dr':
            stdout, _ = utils.runSubprocess('qdel -f %s' % self.id)
        else:
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
        self.finishedJobs = list()
        
        self.updateState()

    #-------------------------------------------------------------------------
    @classmethod
    def connectResources(cls, resources):
        cls.resources = resources
        
    #--------------------------------------------------------------------------
    
    def updateState(self):
        
        ''' Jobs are sorted according to solver type and by their queue state '''
        
        self.jobs = list()
        
        self.jobsBySolver = dict()
        for solverType in bi.SOLVER_TYPES.values():
            self.jobsBySolver[solverType] = list()
        
        for job in self.resources.jobsInQueue.values():
            solverType = job.solverType
            if job['state'] == 'r':
                self.jobsBySolver[solverType].insert(0, job)
            else:
                self.jobsBySolver[solverType].append(job)
        
        for jobs in self.jobsBySolver.values():
            self.jobs.extend(jobs)
    
    #--------------------------------------------------------------------------
    
    def getJobsInQueue(self):
        
        return self.resources.jobsInQueue.values()
                    
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

    
    