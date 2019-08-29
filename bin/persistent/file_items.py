#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Python script for '''

import os
import sys
import glob
from string import Template

from domain import enum_items as ei


#==============================================================================

class InpFileException(Exception): pass

#==============================================================================

class AbaqusInpFileException(Exception): pass

#==============================================================================

class PamCrashInpFileException(Exception): pass

#==============================================================================

class NastranInpFileException(Exception): pass

#==============================================================================

class AbaqusInpFile(object):
    
    ANALYSIS_CONTENT_FILE_EXTS = ['*.res', '*.mdl', '*.stt', '*.prt', '*.odb',
        '*.abq', '*.pac', '*.sel', '*.sim']
    
    def __init__(self, inpFileName):

        self.fileName = inpFileName
        self.baseName = os.path.splitext(os.path.basename(inpFileName))[0]
        self.dirName = os.path.dirname(inpFileName)
        
        self.includeFiles = list()
        self.fillFiles = list()
        
        self.stepPerturbation = False
        self.dynamicsExplicit = False
        self.eigSolver = None
        self.subAllFiles = False
        self.retAllFiles = False
                
        self._analyseContent()
        self._checkIncludedFiles(self.includeFiles)
        self._checkIncludedFiles(self.fillFiles)
                
    #-------------------------------------------------------------------------
    
    def _analyseContent(self):
        
        fi = open(self.fileName, 'rt')
        
        for line in fi.readlines():
            # line with commands is non-case sensitive except parameters
            rawLine = line
            line = line.upper()
            if line.startswith('*INCLUDE'):
                parts = rawLine.split()
                includePart = parts[-1].strip()
                includeFile = includePart.split('=')[-1]
                
                self.includeFiles.append(includeFile)            
            elif line.startswith('*STEP'):
                if 'PERTURBATION' in line:
                    self.stepPerturbation = True
            elif line.startswith('*DYNAMIC'):
                if 'EXPLICIT' in line:
                    self.dynamicsExplicit = True
            elif line.startswith('*RESTART'):
                if 'READ' in line:
                    self.subAllFiles = True
                elif 'WRITE' in line:
                    self.retAllFiles = True
            elif 'FILE=' in line and '.fil' in line:
                parts = rawLine.split()
                fillPart = parts[-1].strip()
                fillFile = fillPart.split('=')[-1]               
                self.fillFiles.append(fillFile)
            elif '*FREQUENCY' in line:
                parts = line.split(',')
                for part in parts:
                    if 'EIGENSOLVER' in part:
                        params = part.split('=')
                        self.eigSolver = params[-1].strip()
            
        fi.close()

    #-------------------------------------------------------------------------
    
    def _checkIncludedFiles(self, filesNames):
      
        for includedFile in filesNames:
            includedFileAbs = os.path.normpath(os.path.join(self.dirName, includedFile))
            
            if not os.path.exists(includedFileAbs):
                message = 'File defined in the input file does not exist!'
                message += '\nMissing file: %s' % includedFileAbs
                raise InpFileException(message)
                   
    #-------------------------------------------------------------------------
    
    def getExistingAnalysisFileNames(self):
        
        fileNames = [self.fileName, ]
        for fileExt in self.ANALYSIS_CONTENT_FILE_EXTS:
            fileNames.extend(glob.glob(os.path.join(self.dirName, fileExt)))
        
        return fileNames
    
    #-------------------------------------------------------------------------

#==============================================================================

class PamCrashInpFile(AbaqusInpFile):
        
    def __init__(self, pcFileName):

        self.fileName = pcFileName
        self.baseName = os.path.splitext(os.path.basename(pcFileName))[0]
        self.dirName = os.path.dirname(pcFileName)
        
        self.includeFiles = list()
        self.analysisType = None
        self.subAllFiles = False
        self.dataCheck = False
                
        self._analyseContent()
        self._checkIncludedFiles(self.includeFiles)
        
    #-------------------------------------------------------------------------
    
    def _analyseContent(self):
        
        fi = open(self.fileName, 'rt')
        
        for line in fi.readlines():
            # line with commands is non-case sensitive except parameters
            rawLine = line
            line = line.upper()
            if line.startswith('INCLU'):
                parts = rawLine.split()
                includeFile = parts[-1].strip()
#                 includeFileParts = includePart.split('/')[1:]
#                 includeFile = '/'.join(includeFileParts)
                
                self.includeFiles.append(includeFile)
            elif line.startswith('ANALYSIS'):
                parts = line.split()
                try:
                    self.analysisType = ei.AnalysisTypes.PAMCRASH[parts[1].strip()]
                except Exception as e:
                    raise PamCrashInpFileException(
                         'Unknown analysis type: %s' % line)
            elif line.startswith('TITLE'):
                parts = rawLine.split()
                title = parts[-1].strip()
                if title != self.baseName:
                    raise PamCrashInpFileException(
                        'TITLE parameter is not consistent with the given file name!\n"%s" != "%s".\nThis may cause unwanted overwriting of existing results!' % (
                            title, self.baseName))
            elif line.startswith('DATACHECK'):
                parts = [p.strip() for p in line.split()]
                if len(parts) == 3 and parts[1] == 'YES' and parts[2] == 'QUIT':
                    self.dataCheck = True

        fi.close()
    
    #-------------------------------------------------------------------------
    
    def switchDataCheckMode(self):
        
        fi = open(self.fileName, 'rt')
                
        content = list()
        for line in fi.readlines():
            # line with commands is non-case sensitive except parameters
            rawLine = line
            line = line.upper()            
            if line.startswith('DATACHECK'):
                parts = [p.strip() for p in line.split()]
                
                # data check present - removing
                if len(parts) == 3 and parts[1] == 'YES' and parts[2] == 'QUIT':
                    rawLine = 'DATACHECK YES\n'
                    self.dataCheck = False
                    
                # data check not present - adding
                else:
                    rawLine = 'DATACHECK YES QUIT\n'
                    self.dataCheck = True
            content.append(rawLine)
        fi.close()
        
        # write a new file
        fo = open(self.fileName, 'wt')
        for line in content:
            fo.write(line)
        fo.close()
        

#==============================================================================

class NastranInpFile(AbaqusInpFile):
        
    def __init__(self, bdfFileName):

        self.fileName = bdfFileName
        self.baseName = os.path.splitext(os.path.basename(bdfFileName))[0]
        self.dirName = os.path.dirname(bdfFileName)
        
        self.includeFiles = list()
        self.subAllFiles = False
                
        self._analyseContent()
        self._checkIncludedFiles(self.includeFiles)
    
    #-------------------------------------------------------------------------
    
    def _analyseContent(self):
        
        fi = open(self.fileName, 'rt')
        
        for line in fi.readlines():
            # line with commands is non-case sensitive except parameters
            rawLine = line
            line = line.upper()
            if line.startswith('INCLUDE'):
                parts = rawLine.split()
                includeFile = parts[-1].strip('"').strip("'")
                              
                self.includeFiles.append(includeFile)
            

#==============================================================================

class ToscaInpFile(AbaqusInpFile):
    
    def __init__(self, parFileName):
        
        self.fileName = parFileName
        self.baseName = os.path.splitext(os.path.basename(parFileName))[0]
        self.dirName = os.path.dirname(parFileName)
        
        self.includeFiles = list()
        self.subAllFiles = False
                
        self._analyseContent()
        self._checkIncludedFiles(self.includeFiles)
    
    #-------------------------------------------------------------------------
    
    def _analyseContent(self):
        
        fi = open(self.fileName, 'rt')
        
        for line in fi.readlines():
            # line with commands is non-case sensitive except parameters
            rawLine = line
            line = line.upper().strip()
            if line.startswith('FILE'):
                parts = rawLine.split('=')
                includeFile = parts[-1].strip()
                              
                self.includeFiles.append(includeFile)
    
#==============================================================================

class AbaqusEnvConfigFile(object):    
    
    def __init__(self, parentJob):
        
        self.parentJob = parentJob

#==============================================================================

class AbaqusJobExecutableFile(object):
    
#     SOLVER_NAME = 'ABAQUS'
    
    def __init__(self, parentApplication, parentJob):
        
        self.parentApplication = parentApplication
        
        self.parentJob = parentJob
        self.parentProfile = self.parentApplication.profile
        
        self.jobSettings = self.parentProfile.jobSettings
        self.user = self.parentProfile.user
        self.postProcessingType = self.parentApplication.profile.postProcessingType
        
        self.outputFileName = os.path.join(self.parentJob.inpFile.dirName,
            self.parentJob.inpFile.baseName + '.sh')
        
    #-------------------------------------------------------------------------

    def getContent(self):
        
        content = self._getDescriptionContent()

        content += '\n/bin/uname -a\n\n'
        content += 'echo "Starting %s"\n' % self.parentProfile.SOLVER_TYPE.NAME
        content += self._getRunCommand()
        content += 'echo "%s finished with the status:" $?\n\n' % self.parentProfile.SOLVER_TYPE.NAME
        content += '# now sleep until lock file disappears\n'
        content += 'sleep 30 && while [ -f %s.lck ]; do sleep 5; done\n' % self.parentJob.inpFile.baseName
        content += self.postProcessingType.getContent(self.parentJob)
        
        return content
    
    #-------------------------------------------------------------------------
    
    def save(self):
                
        fo = open(self.outputFileName, 'wt')
        fo.write(self.getContent())
        fo.close()
        
    #-------------------------------------------------------------------------
    
    def _getRunCommand(self):
                
        runCommand = '%s job=%s scratch=%s' % (
            self.parentJob.solverVersion,
            self.parentJob.inpFile.baseName,
            self.jobSettings.SCRATCH_SERVER_PATH)
        
        if self.parentJob.numberOfCores > 1:
            # explicit calculation
            if self.parentJob.inpFile.dynamicsExplicit:
                runCommand += ' parallel=domain cpus=%s domains=%s' % (
                    self.parentJob.numberOfCores, self.parentJob.numberOfCores)
            
            # standard calculation
            else:
                # GPU settings
                if self.parentJob.numberOfGPUCores:
                    if '6141' in self.parentJob.solverVersion:
                        runCommand += ' cpus=%s mp_mode=mpi gpu=nvidia' % (
                            self.parentJob.numberOfCores)
                    else:
                        runCommand += ' cpus=%s gpus=%s' % (
                            self.parentJob.numberOfCores, self.parentJob.numberOfGPUCores)
                else:
                    runCommand += ' cpus=%s' % self.parentJob.numberOfCores
        
        # add restart file
        if self.parentJob.restartInpFile is not None:
            runCommand += ' oldjob=%s' % self.parentJob.restartInpFile.baseName
        
        runCommand += ' %s' % self.jobSettings.additionalSolverParams
        
        return '%s\n' % runCommand
    
    #-------------------------------------------------------------------------
    
    def _getDescriptionContent(self):
        
        content = '#!/bin/bash\n'
#         content += '#$ -hard -l %s\n' % self._getJobFeatures()
        content += '#$ -hard -l %s' % self._getJobFeatures()
        content += ' -l excl=true -l hostname=%s\n' % self.jobSettings.executionServer.fullName[1:]       
        content += '#$ -q %s@*\n' % self.jobSettings.licenseServer.CODE
#         content += '#$ -soft -q %s%s\n' % (self.jobSettings.licenseServer.CODE, self.jobSettings.executionServer.fullName)
        content += '#$ -cwd \n'
        content += '#$ -j y\n'
        content += '#$ -N %s\n' % self.parentJob.inpFile.baseName
        content += '#$ -p %s\n' % self.parentJob.priority
        content += '#$ -v ver_solver=%s\n' % self.parentJob.solverVersion
        content += '#$ -v sub_allfiles=%s\n' % int(self.parentJob.inpFile.subAllFiles)
        content += '#$ -v ret_allfiles=%s\n' % int(self.parentJob.inpFile.retAllFiles)
        content += '#$ -ac verze=%s\n' % self.parentJob.solverVersion
        content += '#$ -ac popis_ulohy=%s\n' % self.parentJob.description
        content += '#$ -a %s\n' % self.parentJob.startTime
        if len(self.user.email) > 0:
            content += '#$ -M %s\n' % self.user.email
            content += '#$ -m beas\n'
        
        if self.parentJob.inpFile.subAllFiles:
            content += '#$ -v jobname_old=%s\n' % self.parentJob.restartInpFile.baseName
        
        content += 'umask 0002\n'
        
        content += 'scratch_dir=%s/%s/$JOB_NAME.$JOB_ID\n' % (
            self.jobSettings.SCRATCH_PATH, self.user.name)
        content += 'cd $scratch_dir\n'
        
        return content
        
    #--------------------------------------------------------------------------
    
    def _getJobFeatures(self):
        
        features = '%s=%s' % (self.jobSettings.licenseServer.QUEUE_CODE,
                self.parentJob.getTokensRequired())
        
        return features
    
    #--------------------------------------------------------------------------
    
#     def _getMetaDbExportContent(self):
#         
#         template = Template('''/bin/uname -a
# # now sleep until lock file disappears
# sleep 30 && while [ -f $jobname.lck ]; do sleep 5; done
# 
# if [ -r META_queue_session.ses -a -f /usr1/applications/ansa/BETA_CAE_Systems/meta_post_v18.1.1/meta_post64.sh ]; then   #konverze do metadb
#     echo "Startuji konverzi do Metadb"
#     echo "Startuji konverzi do Metadb" >> $jobname.log
#     /usr1/applications/ansa/BETA_CAE_Systems/meta_post_v18.1.1/meta_post64.sh -b -foregr -virtualx_64bit -s META_queue_session.ses $jobname &>> $jobname.log
#     sleep 5
#     echo "Koncim konverzi do Metadb"
#     echo "Koncim konverzi do Metadb" >> $jobname.log
# fi
# ''')
#         
#         
#         return template.safe_substitute(
#             {'jobname' : self.parentJob.inpFile.baseName})

#==============================================================================

class PamCrashJobExecutableFile(AbaqusJobExecutableFile):
    
#     SOLVER_NAME = 'PAMCRASH'

    #-------------------------------------------------------------------------

    def getContent(self):
        
        content = self._getDescriptionContent()

        content += '\n/bin/uname -a\n\n'
        content += 'echo "Starting %s"\n' % self.parentProfile.SOLVER_TYPE.NAME
        content += self._getRunCommand()
        content += 'echo "%s finished with the status:" $?\n\n' % self.parentProfile.SOLVER_TYPE.NAME
        content += '# now sleep\n'
        content += 'sleep 10\n'
        content += self.postProcessingType.getContent(self.parentJob)
        
        return content
    
    #-------------------------------------------------------------------------
    
    def _getRunCommand(self):
        
        
        runCommand = ''
        runCommand += 'export PAM_LMD_LICENSE_FILE=7789@mb-dc1\n'
        runCommand += 'export PAMHOME=%s/\n' % os.path.dirname(
            os.path.dirname(self.parentJob.solverVersion))
        
        runCommand += '%s -np %s -lic CRASHSAF' % (
            self.parentJob.solverVersion, self.parentJob.numberOfCores)
        
        if self.parentJob.inpFile.analysisType == ei.AnalysisTypes.IMPLICIT:
            runCommand += ' -fp 2'
        
        runCommand += ' %s' % self.jobSettings.additionalSolverParams
        runCommand += ' %s.pc > %s.pc.out' % (
            self.parentJob.inpFile.baseName, self.parentJob.inpFile.baseName)
        
        return '%s\n' % runCommand

    #-------------------------------------------------------------------------
    
    def _getDescriptionContent(self):
        
        content = '#!/bin/bash\n'
        content += '#$ -hard -l %s' % self._getJobFeatures()
        content += ' -l excl=true -l hostname=%s\n' % self.jobSettings.executionServer.fullName[1:]
        content += '#$ -q %s@*\n' % self.jobSettings.licenseServer.CODE
#         content += '#$ -soft -q %s%s\n' % (self.jobSettings.licenseServer.CODE, self.jobSettings.executionServer.fullName)
        content += '#$ -cwd -V\n'
        content += '#$ -j y\n'
        content += '#$ -N %s\n' % self.parentJob.inpFile.baseName
        content += '#$ -p %s\n' % self.parentJob.priority
        content += '#$ -ac popis_ulohy=%s\n' % self.parentJob.description
        content += '#$ -a %s\n' % self.parentJob.startTime
        if len(self.user.email) > 0:
            content += '#$ -M %s\n' % self.user.email
            content += '#$ -m beas\n'
                            
        content += 'scratch_dir=%s/%s/$JOB_NAME.$JOB_ID\n' % (
            self.jobSettings.SCRATCH_PATH, self.user.name)
        content += 'cd $scratch_dir\n'
        
        return content
    
    #--------------------------------------------------------------------------
    
#     def _getJobFeatures(self):
#         
#         features = '%s=%s' % (self.jobSettings.licenseServer.CODE,
#                 self.parentJob.getTokensRequired())
#         
#         return features

#==============================================================================

class NastranJobExecutableFile(PamCrashJobExecutableFile):
    
    #-------------------------------------------------------------------------
    
    def _getRunCommand(self):
        
        
        runCommand = ''
        runCommand += '%s' % self.parentJob.solverVersion
        
        runCommand += ' %s' % self.jobSettings.additionalSolverParams
        runCommand += ' %s.bdf > %s.bdf.out' % (
            self.parentJob.inpFile.baseName, self.parentJob.inpFile.baseName)        
                
        return '%s\n' % runCommand
    
    #--------------------------------------------------------------------------
    
    def _getJobFeatures(self):
        
        features = '%s=%s' % (self.jobSettings.licenseServer.CODE,
                self.parentJob.getTokensRequired())
        
        return features
    
#==============================================================================

class ToscaJobExecutableFile(PamCrashJobExecutableFile):
    
    #-------------------------------------------------------------------------
    
    def _getRunCommand(self):
        
        runCommand = ''
        runCommand += '%s -cpus %s -scpus %s' % (self.parentJob.toscaSolverVersion,
            self.parentJob.numberOfCores, self.parentJob.numberOfSolverCores)
        
        runCommand += ' %s' % self.jobSettings.additionalSolverParams
        runCommand += ' %s.par > %s.par.out' % (
            self.parentJob.inpFile.baseName, self.parentJob.inpFile.baseName)        
                
        return '%s\n' % runCommand
    
