#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import traceback

from PyQt4 import QtCore, QtGui

from domain import utils
from domain import base_items as bi
from domain import comp_items as ci
from domain import enum_items as ei
import base_widgets as bw

#===============================================================================

SUBMIT_WIDGET_TYPES = list()

#=============================================================================

def saveExecute(method, *args):
    
    def wrapper(*args):
        
        parentApplication = args[0].parentApplication
        parentApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            method(*args)
        except Exception as e:
            traceback.print_exc()
            parentApplication.restoreOverrideCursor()
            
            QtGui.QMessageBox.critical(
                parentApplication.mainWindow, '%s' % parentApplication.APPLICATION_NAME,
                str(e))
        
        parentApplication.restoreOverrideCursor()
        
    return wrapper

#===============================================================================

class CentralWidget(QtGui.QWidget):
    
    def __init__(self, mainWindow):
        super(CentralWidget, self).__init__()
        
        self.mainWindow = mainWindow 
        self.parentApplication = mainWindow.parentApplication
        
        self._setupWidgets()
        self._setupConnections()
            
    #--------------------------------------------------------------------------

    def _setupWidgets(self):
                        
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)
        
        self.tabWidget = QtGui.QTabWidget(self)
        
        self.layout.addWidget(self.tabWidget)
        
        self.queueTabWidget = QueueWidget(self)
        
        self.tabWidget.addTab(self.queueTabWidget, 'Queue')
        
        for submitWidgetType in SUBMIT_WIDGET_TYPES:
            submitWidget = submitWidgetType(self)
            self.tabWidget.addTab(submitWidget, submitWidget.NAME)
                
    #--------------------------------------------------------------------------

    def _setupConnections(self):
    
        pass   

#===============================================================================

class QueueWidget(QtGui.QWidget):
    
    def __init__(self, parentCentralWidget):
        super(QueueWidget, self).__init__()
        
        self.parentCentralWidget = parentCentralWidget
        self.parentApplication = parentCentralWidget.parentApplication
        
        self.queue = self.parentApplication.q
        
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)
                
        labels = QtGui.QLabel(self.queue.getColumnLabels())
        font = QtGui.QFont()
        font.setFamily("Courier New")
        labels.setFont(font)             
        self.layout.addWidget(labels)
        
        self.queueListWidget = bw.QueueListWidget(self)
        self.layout.addWidget(self.queueListWidget)
                    
    #--------------------------------------------------------------------------
    
    def updateContent(self):
                
        self.queueListWidget.clear()
        
        for job in self.queue.jobs:
            newItem = bw.QueueJobListWidgetItem(job)
            
            self.queueListWidget.addItem(newItem)
            
            
     
#===============================================================================

class BaseSubmitWidget(QtGui.QWidget):
    
    container = SUBMIT_WIDGET_TYPES

    def __init__(self, parentCentralWidget):
        super(BaseSubmitWidget, self).__init__()
        
        self.parentCentralWidget = parentCentralWidget 
        self.parentApplication = parentCentralWidget.parentApplication
        
#         self.workDir = '/data/fem/users/siegl/eclipse/qaba/res/test_files/ABAQUS'
        self.workDir = os.getcwd()
        
#         self.jobs = list()
        self.profile = None
        
        self._setupWidgets()
        self._setupConnections()
        
        # initialise
        self._initiateOptions()
    
    #---------------------------------------------------------------------------
    
    def _initiateOptions(self):
        
#         self._findInputFiles(self.getWorkDir())
        
        self.profileSelectorWidget.setupOptions()
        self.licenseServerSelectorWidget.setupOptions()
#         self.executionServerSelectorWidget.setupOptions()
        
        self._findInputFiles(self.getWorkDir())
        
        self.licenseServerSelectorWidget.setDefaultOption(
            self.profile.getDftLicenseServerOption())
        
        self.solverVersionSelectorWidget.setupOptions()
        
        self.jobPrioritySelectorWidget.setDefaultOption(
            *self.profile.getDftJobPriority())
                    
    #---------------------------------------------------------------------------
    
    def setWorkDir(self, path):
        
        self.workDir = path

    #---------------------------------------------------------------------------
        
    def getWorkDir(self):
        return self.workDir

    #---------------------------------------------------------------------------
    @saveExecute
    def submit(self):
                
        if len(self.profile.inpFileNames) == 0:
            raise bi.DataSelectorException('No files selected!')
        
        message = ''
        for inpFileName in self.profile.inpFileNames:
            newJob = self.profile.job.getCopy()
            newJob.setInpFile(inpFileName)
            newJob.setExecutableFile(newJob.EXECUTABLE_FILE_TYPE(self, newJob))
            newJob.executableFile.save()
#             self.jobs.append(newJob)
            
            # in case of restart read
            if newJob.inpFile.subAllFiles:
                restartInpFileName = QtGui.QFileDialog.getOpenFileName(self,
                    'Select restart input file', newJob.inpFile.dirName,
                     filter = "Input file for analysis: '%s' (*%s)" % (
                        newJob.inpFile.baseName, ei.FileExtensions.ABAQUS_INPUT))
                 
                if not restartInpFileName:
                    raise bi.DataSelectorException('No restart file selected!')
                
                print '\tSelected restart file: %s' % restartInpFileName
                         
                info = newJob.setRestartInpFile(str(restartInpFileName))
                print info
                message = 'Restart files status:'
                for baseName, status in info.iteritems():
                    message += '\n%s: %s' % (baseName, status)
                
                self.parentApplication.showInfoMessage(message)                
                
            message += 'Submitting job: %s\n' % newJob.inpFile.baseName
            
            if self.parentApplication.DEBUG:
                print newJob.executableFile.getContent()
            else:
                utils.runSubprocess('qsub %s' % newJob.executableFile.outputFileName)
        
        self.parentApplication.showInfoMessage(message)
                
    #--------------------------------------------------------------------------

    def _setupWidgets(self):
        
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)
        
        mainSplitter = QtGui.QSplitter()
        mainSplitter.setOrientation(QtCore.Qt.Horizontal)
        self.layout.addWidget(mainSplitter)
        
        leftPaneWidget = QtGui.QWidget()
        leftPaneWidget.setLayout(QtGui.QVBoxLayout())
        rightPaneWidget = QtGui.QWidget()
        rightPaneWidget.setLayout(QtGui.QVBoxLayout())
        
        mainSplitter.addWidget(leftPaneWidget)
        mainSplitter.addWidget(rightPaneWidget)
        
        # add selectors        
        # right pane
#         selectorItem = bi.InputFileSelector(self)
#         self.workingDirectorySelectorWidget = bw.WorkingDirectorySelectorWidget(selectorItem)
#         rightPaneWidget.layout().addWidget(self.workingDirectorySelectorWidget)
        
        selectorItem = ci.AbaqusExecutionProfileSelector(self)
        self.profileSelectorWidget = bw.BaseSelectorWidget(selectorItem)
        rightPaneWidget.layout().addWidget(self.profileSelectorWidget)
                
        selectorItem = bi.LicenseServerSelector(self)
        self.licenseServerSelectorWidget = bw.BaseSelectorWidget(selectorItem)
        rightPaneWidget.layout().addWidget(self.licenseServerSelectorWidget)
        
        selectorItem = bi.SolverVersionSelector(self)
        self.solverVersionSelectorWidget = bw.BaseSelectorWidget(selectorItem)
        rightPaneWidget.layout().addWidget(self.solverVersionSelectorWidget)
        
        groupLayout = QtGui.QVBoxLayout()
        group = QtGui.QGroupBox('Parameters')
        group.setLayout(groupLayout)
        rightPaneWidget.layout().addWidget(group)
        
        self.noOfCoresSelectorWidget = bw.NoOfCoresSelectorWidget()
        groupLayout.addWidget(self.noOfCoresSelectorWidget)
        
        self.noOfGpusSelectorWidget = bw.NoOfGpusSelectorWidget()
        groupLayout.addWidget(self.noOfGpusSelectorWidget)
        
        self.jobPrioritySelectorWidget = bw.JobPrioritySelectorWidget()
        groupLayout.addWidget(self.jobPrioritySelectorWidget)
        
        self.jobDescriptionSelectorWidget = bw.JobDescriptionSelectorWidget()
        groupLayout.addWidget(self.jobDescriptionSelectorWidget)
        
        self.solverParametersSelectorWidget = bw.SolverParametersSelectorWidget()
        groupLayout.addWidget(self.solverParametersSelectorWidget)
        
        self.jobStartTimeSelectorWidget = bw.JobStartTimeSelectorWidget()
        groupLayout.addWidget(self.jobStartTimeSelectorWidget)
        
        
        
        # left pane
        selectorItem = bi.InputFileSelector(self)
        self.inputFileSelectorWidget = bw.InputFileSelectorWidget(selectorItem)
        leftPaneWidget.layout().addWidget(self.inputFileSelectorWidget)
        
        selectorItem = bi.ExecutionServerSelector(self)
        self.executionServerSelectorWidget = bw.ExecutionServerSelectorWidget(selectorItem)
        leftPaneWidget.layout().addWidget(self.executionServerSelectorWidget)
        
        rightPaneWidget.layout().addStretch()
#         rightPaneWidget.layout().addStretch()
#         self.layout.addStretch()
        
        buttonLayout = QtGui.QHBoxLayout()
        self.layout.addLayout(buttonLayout)
        buttonLayout.addStretch()
                
        self.submitButton = QtGui.QPushButton('Submit')
        buttonLayout.addWidget(self.submitButton)
    
    #--------------------------------------------------------------------------

    def _setupConnections(self):
    
        self.profileSelectorWidget.changed.connect(self._setupProfile)
        self.solverVersionSelectorWidget.changed.connect(self._setSolverVersion)
        self.licenseServerSelectorWidget.changed.connect(self._setupLicenseServer)
        self.executionServerSelectorWidget.changed.connect(self._setExecutionServer)
#         self.workingDirectorySelectorWidget.changed.connect(self._findInputFiles)
        
        self.inputFileSelectorWidget.changed.connect(self._setupInputFiles)
        
        self.noOfCoresSelectorWidget.changed.connect(self._setNumberOfCores)
        self.noOfGpusSelectorWidget.changed.connect(self._setNumberOfGPUCores)
        self.jobPrioritySelectorWidget.changed.connect(self._setJobPriority)
        self.jobDescriptionSelectorWidget.changed.connect(self._setJobDescription)
        self.solverParametersSelectorWidget.changed.connect(self._setAdditionalSolverParams)
        self.jobStartTimeSelectorWidget.changed.connect(self._setJobStartTime)
        
        self.submitButton.released.connect(self.submit)
        
    #--------------------------------------------------------------------------
 
    def _findInputFiles(self, projectDir):
 
#         self.setWorkDir(projectDir)
         
        self.inputFileSelectorWidget.findInputFiles(projectDir)
         
        self.inputFileSelectorWidget.setupInputFiles()
            
    #--------------------------------------------------------------------------

    def _setupInputFiles(self, inputFiles):
        
        self.profile.inpFileNames = inputFiles
        
        if len(inputFiles) > 0:
            self.profile.job.setInpFile(inputFiles[0])
                            
            # check analysis type
            self.noOfGpusSelectorWidget.setDefaultOption(*self.profile.getDftNoOfGpus())
        else:
            self.noOfGpusSelectorWidget.setDefaultOption(0, 0, 0)
        
    #--------------------------------------------------------------------------
    
    def _setupProfile(self, profile):
        
        # initialisation or switching the current profile
        if self.profile is None:
            self.profile = profile(self)
            
        else:
            currentJob = self.profile.job
            currentSettings = self.profile.jobSettings
            currentInpFileNames = self.profile.inpFileNames
            
            self.profile = profile(self)
            self.profile.job = currentJob
            self.profile.jobSettings = currentSettings
            self.profile.inpFileNames = currentInpFileNames
        
        self.licenseServerSelectorWidget.setDefaultOption(
            self.profile.getDftLicenseServerOption())
        
        print 'Setting current profile to: %s' % self.profile.NAME
        
    #--------------------------------------------------------------------------

    def _setupLicenseServer(self, licenseServer):
        
        self.profile.jobSettings.setLicenseServer(licenseServer)
        
        # update execution server list
        self.executionServerSelectorWidget.setupOptions()
        self.executionServerSelectorWidget.setDefaultOption(
            self.profile.getDftExectionServerOption())
    
    #--------------------------------------------------------------------------

    def _setExecutionServer(self, executionServer):
        
        self.profile.jobSettings.setExecutionServer(executionServer)
        
        self.noOfCoresSelectorWidget.setDefaultOption(*self.profile.getDftNoOfCores())
        
        if self.profile.job.inpFile is not None:
            self.noOfGpusSelectorWidget.setDefaultOption(*self.profile.getDftNoOfGpus())
        else:
            self.noOfGpusSelectorWidget.setDefaultOption(0, 0, 0)
                
    #--------------------------------------------------------------------------

    def _setSolverVersion(self, solverVersion):
        
        self.profile.job.setSolverVersion(solverVersion)
    
    #--------------------------------------------------------------------------
    
    def _setNumberOfCores(self, numberOfCores):
                
        self.profile.job.setNumberOfCores(numberOfCores)
    
    #--------------------------------------------------------------------------
    
    def _setNumberOfGPUCores(self, numberOfGPUCores):        
        
        self.profile.job.setNumberOfGPUCores(numberOfGPUCores)
    
    #--------------------------------------------------------------------------
    
    def _setJobPriority(self, priority):        
                          
        self.profile.job.setPriority(priority)   
    
    #--------------------------------------------------------------------------
    
    def _setJobStartTime(self, jobStartTime):
                        
        self.profile.job.setStartTime(jobStartTime)
    
    #--------------------------------------------------------------------------
    
    def _setAdditionalSolverParams(self, params):
        
        self.profile.jobSettings.setAdditionalSolverParams(params)
    
    #--------------------------------------------------------------------------
    
    def _setJobDescription(self, jobDescription):
                        
        self.profile.job.setDescription(jobDescription)
        
#===============================================================================
@utils.registerClass
class AbaqusSubmitWidget(BaseSubmitWidget):
    
    ID = 0
    NAME = 'Submit ABAQUS'
    

    
#===============================================================================
@utils.registerClass
class PamCrashSubmitWidget(BaseSubmitWidget):
    
    ID = 1
    NAME = 'Submit PAMCRASH'
    
    #--------------------------------------------------------------------------

    def _setupWidgets(self):
        
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)
        
        mainSplitter = QtGui.QSplitter()
        mainSplitter.setOrientation(QtCore.Qt.Horizontal)
        self.layout.addWidget(mainSplitter)
        
        leftPaneWidget = QtGui.QWidget()
        leftPaneWidget.setLayout(QtGui.QVBoxLayout())
        rightPaneWidget = QtGui.QWidget()
        rightPaneWidget.setLayout(QtGui.QVBoxLayout())
        
        mainSplitter.addWidget(leftPaneWidget)
        mainSplitter.addWidget(rightPaneWidget)
        
        # add selectors        
        # right pane
        selectorItem = bi.PamcrashInputFileSelector(self)
        self.workingDirectorySelectorWidget = bw.WorkingDirectorySelectorWidget(selectorItem)
        rightPaneWidget.layout().addWidget(self.workingDirectorySelectorWidget)
        
        selectorItem = ci.PamCrashExecutionProfileSelector(self)
        self.profileSelectorWidget = bw.BaseSelectorWidget(selectorItem)
        rightPaneWidget.layout().addWidget(self.profileSelectorWidget)
                
        selectorItem = bi.PamCrashLicenseServerSelector(self)
        self.licenseServerSelectorWidget = bw.BaseSelectorWidget(selectorItem)
        rightPaneWidget.layout().addWidget(self.licenseServerSelectorWidget)
        
        selectorItem = bi.PamCrashSolverVersionSelector(self)
        self.solverVersionSelectorWidget = bw.BaseSelectorWidget(selectorItem)
        rightPaneWidget.layout().addWidget(self.solverVersionSelectorWidget)
        
        groupLayout = QtGui.QVBoxLayout()
        group = QtGui.QGroupBox('Parameters')
        group.setLayout(groupLayout)
        rightPaneWidget.layout().addWidget(group)
        
        self.noOfCoresSelectorWidget = bw.NoOfCoresSelectorWidget()
        groupLayout.addWidget(self.noOfCoresSelectorWidget)
        
        self.noOfGpusSelectorWidget = bw.NoOfGpusSelectorWidget()
        groupLayout.addWidget(self.noOfGpusSelectorWidget)
        
        self.jobPrioritySelectorWidget = bw.JobPrioritySelectorWidget()
        groupLayout.addWidget(self.jobPrioritySelectorWidget)
        
        self.jobDescriptionSelectorWidget = bw.JobDescriptionSelectorWidget()
        groupLayout.addWidget(self.jobDescriptionSelectorWidget)
        
        self.solverParametersSelectorWidget = bw.SolverParametersSelectorWidget()
        groupLayout.addWidget(self.solverParametersSelectorWidget)
        
        self.jobStartTimeSelectorWidget = bw.JobStartTimeSelectorWidget()
        groupLayout.addWidget(self.jobStartTimeSelectorWidget)
        
        
        
        # left pane
        selectorItem = bi.PamcrashInputFileSelector(self)
        self.inputFileSelectorWidget = bw.InputFileSelectorWidget(selectorItem)
        leftPaneWidget.layout().addWidget(self.inputFileSelectorWidget)
        
        selectorItem = bi.PamCrashExecutionServerSelector(self)
        self.executionServerSelectorWidget = bw.ExecutionServerSelectorWidget(selectorItem)
        leftPaneWidget.layout().addWidget(self.executionServerSelectorWidget)
        
        rightPaneWidget.layout().addStretch()
#         rightPaneWidget.layout().addStretch()
#         self.layout.addStretch()
        
        buttonLayout = QtGui.QHBoxLayout()
        self.layout.addLayout(buttonLayout)
        buttonLayout.addStretch()
                
        self.submitButton = QtGui.QPushButton('Submit')
        buttonLayout.addWidget(self.submitButton)
            
#===============================================================================

