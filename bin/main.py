#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Queue Application
=================

Monitors and submits jobs for Grid Engine. There are multiple input 
interfaces that can control application functionality.

Input interface
---------------

* qq - graphical interface
* q  - text based overview of Grid Engine jobs statuses 
* qa + no input parameters - text based interactive submit for ABAQUS
* qa + input parameters - command line based submit for ABAQUS
* qp + no input parameters - text based interactive submit for PAMCRASH
* qp + input parameters - command line based submit for PAMCRASH

Job submitting
--------------

is based on execution profiles that provide default options (based on 
available resources), standard preferred execution settings or 
can simplify input parameters (e.g. datacheck).

Usage
=====

qq
--

graphical interface providing the complete tool functionality::

    qq

Queue monitor:

.. image:: images/qq_01.png
    :width: 600pt
    :align: center

Submitting tools:

.. image:: images/qq_02.png
    :width: 600pt
    :align: center

q
--

.. image:: images/q_01.png
    :width: 600pt
    :align: center

text based overview of Grid Engine jobs statuses::

    q

qa
--

.. image:: images/qa_01.png
    :width: 600pt
    :align: center

submits ABAQUS job to Grid Engine::

    qa [-h] [-inp [inp_path [inp_path ...]]]
               [-license {COMMERCIAL,VAR_2,VAR_1}]
               [-solver {abaqus6141,abaqus2016x,abaqus2017x,abaqus2018x,abaqus2018-HF4}]
               [-host {hk-u1,hk-u3,hk-u4,hk-u5,lb-u1,lb-u2,lb-u3,mb-so1,mb-so2,mb-u13,mb-u14,mb-u15,mb-u16,mb-u17,mb-u18,mb-u19,mb-u20,mb-u21,mb-u22,mb-u23,mb-u24,mb-u26}]
               [-cpu CPU] [-gpu GPU] [-prio PRIO] [-start START] [-des DES]
               [-param PARAM]
    
    
    optional arguments:
      -h, --help            show this help message and exit
      -inp [inp_path [inp_path ...]]
                            ABAQUS Input file path.
      -license {COMMERCIAL,VAR_2,VAR_1}
                            ABAQUS license server type. (default=COMMERCIAL)
      -solver {abaqus6141,abaqus2016x,abaqus2017x,abaqus2018x,abaqus2018-HF4}
                            ABAQUS solver version. (default=abaqus2017x)
      -host {hk-u1,hk-u3,hk-u4,hk-u5,lb-u1,lb-u2,lb-u3,mb-so1,mb-so2,mb-u13,mb-u14,mb-u15,mb-u16,mb-u17,mb-u18,mb-u19,mb-u20,mb-u21,mb-u22,mb-u23,mb-u24,mb-u26}
                            Calculation host. (default=mb-so2)
      -cpu CPU              Number of CPUs. (default=4)
      -gpu GPU              Number of GPUs. (default=0)
      -prio PRIO            Job priority. (default=50)
      -start START          Job start time. (default=mmddHHMM)
      -des DES              Job description (max. 15 characters).
      -param PARAM          Additional ABAQUS parameters: "-x y -xx yy" (max 15
                            characters).
 
qp
--

submits PAMCRASH job to Grid Engine::

    qp [-h] [-pc inp_path] [-host {mb-so1,mb-so2,mb-so3}] [-cpu CPU]
               [-gpu GPU] [-prio PRIO] [-start START] [-des DES] [-param PARAM]
    
    optional arguments:
      -h, --help            show this help message and exit
      -pc inp_path          PAMCRASH Input file path.
      -host {mb-so1,mb-so2,mb-so3}
                            Calculation host. (default=mb-so3)
      -cpu CPU              Number of CPUs. (default=4)
      -gpu GPU              Number of GPUs. (default=0)
      -prio PRIO            Job priority. (default=50)
      -start START          Job start time. (default=mmddHHMM)
      -des DES              Job description (max. 15 characters).
      -param PARAM          Additional ABAQUS parameters: "-x y -xx yy" (max 15
                            characters).

qn
--

submits NASTRAN job to Grid Engine::

    qn [-h] [-bdf inp_path] [-solver {NASTRAN nas20171}]
              [-host {mb-so1,mb-so2}] [-prio PRIO] [-start START] [-des DES]
              [-param PARAM]
    
    optional arguments:
      -h, --help            show this help message and exit
      -bdf inp_path         NASTRAN Input file path.
      -solver {NASTRAN nas20171}
                            NASTRAN solver version. (default=NASTRAN nas20171)
      -host {mb-so1,mb-so2}
                            Calculation host. (default=mb-so3)
      -prio PRIO            Job priority. (default=50)
      -start START          Job start time. (default=05301530)
      -des DES              Job description (max. 15 characters).
      -param PARAM          Additional ABAQUS parameters: "-x y -xx yy" (max 15
                            characters).


'''

#=========================== to be modified ===================================

APPLICATION_NAME = 'qq'
DOCUMENTATON_GROUP = 'Queue tools'
DOCUMENTATON_DESCRIPTION = 'Python SGE monitoring and submitting application.'

#==============================================================================

import os
import sys
import traceback
import argparse
import time
import logging

from PyQt4 import QtCore, QtGui

from domain import utils
from domain import base_items as bi
from domain import comp_items as ci
from domain import enum_items as ei
from domain import selector_items as si
from domain import profile_items as pi

from presentation import comp_widgets as cw
from presentation import base_widgets as bw


#==============================================================================

DEBUG = 0

#==============================================================================

class QabaException(Exception): pass

#=============================================================================

class QueueApplication(QtGui.QApplication):
    
    APPLICATION_NAME = 'queue application'
    DEBUG = DEBUG
    
    def __init__(self, args):
        
        super(QueueApplication, self).__init__(sys.argv)
        
        self.revision, self.modifiedBy, self.lastModified = utils.getVersionInfo()
        self.userName, self.machine, self.email = utils.getUserInfo()
        
        if DEBUG:
            level = logging.DEBUG
        else:
            level = logging.WARNING
        utils.initiateLogging(self, level)
                
        # connect resources
        ci.Resources.initialise()
        self.q = ci.Queue()       
                
        self.signalGenerator = bw.SignalGenerator()
        
        self.mainWindow = MainWindow(self)
        
        self._setupConnections()
        
        self._updateQueueStatus()
        
        logging.debug(10*'#' + ' Data initialisation completed ' + 10*'#')
                
        self.mainWindow.show()
    
    #---------------------------------------------------------------------------

    def _setupConnections(self):
        
        self.signalGenerator.updateStatus.connect(self._updateQueueStatus)
        self.mainWindow.centralWidget().queueTabWidget.queueTreeView.itemForTrackingSelected.connect(
            self._setupJobTracking)
        
        self.mainWindow.runningJobFileListWidget.itemForTrackingSelected.connect(
            self._setupFileTracking)
    
    #---------------------------------------------------------------------------

    def _updateQueueStatus(self):
        
        ci.Resources.updateState()
        
        self.mainWindow.centralWidget().queueTabWidget.updateContent()
        self.mainWindow.showStatusMessage('Status updated')
    
    #---------------------------------------------------------------------------

    def showInfoMessage(self, message):
        
        self.restoreOverrideCursor()
        
        QtGui.QMessageBox.information(self.mainWindow, '%s' % self.APPLICATION_NAME,
                str(message))
    
    #---------------------------------------------------------------------------

    def _setupJobTracking(self, jobItem):
        
#         self.mainWindow.runningJobFileListDock.setVisible(True)
#         self.mainWindow.setDockGeometry(self.mainWindow.runningJobFileListDock)
        self.mainWindow.runningJobFileListWidget.setupContent(jobItem)
    
    #---------------------------------------------------------------------------

    def _setupFileTracking(self, jobItem, fileName):
        
#         self.mainWindow.fileContentTrackerDock.setVisible(True)
#         self.mainWindow.setDockGeometry(self.mainWindow.fileContentTrackerDock)
        self.mainWindow.fileContentTrackerWidget.setupContent(jobItem, fileName)
        

#===============================================================================

class MainWindow(QtGui.QMainWindow):

    WIDTH = 1500
    HEIGHT = 700
    FONT_POINT_SIZE = 10

    STATUSBAR_MESSAGE_DURATION = 2000
        
    def __init__(self, parentApplication):
        super(MainWindow, self).__init__()

        self.parentApplication = parentApplication
                        
#         self._setupActions()
        self._setupWidgets()

        self._setWindowGeometry()
        self._setupConnections()
        
#         self.runningJobFileListDock.setVisible(False)
#         self.fileContentTrackerDock.setVisible(False)
#         
#         self.runningJobFileListDock.setFloating(True)
#         self.fileContentTrackerDock.setFloating(True)
    
    #---------------------------------------------------------------------------

    def _setWindowGeometry(self):
        
        font = self.font()
        font.setPointSize(self.FONT_POINT_SIZE)
        self.setFont(font)
        
        self.setWindowTitle('%s (%s)' % (
            self.parentApplication.APPLICATION_NAME, self.parentApplication.revision))
        
#         self.setWindowIcon(QtGui.QIcon(os.path.join(utils.PATH_ICONS, 'view-web-browser-dom-tree.png')))

        self.resize(self.WIDTH, self.HEIGHT)
        self.move(QtGui.QApplication.desktop().screen().rect().center()- self.rect().center())

    #--------------------------------------------------------------------------

    def _setupWidgets(self):
                
        self.statusBar()
        
        self.statusBar().addPermanentWidget(
            QtGui.QLabel('Current user: %s@%s' % (
                self.parentApplication.userName, self.parentApplication.machine)))
        
        self.setCentralWidget(cw.CentralWidget(self))
                
        # add docks
        self.runningJobFileListWidget = bw.RunningJobFileListWidget(self)
        self.runningJobFileListDock = bw.createDock(self, 'Job file list', self.runningJobFileListWidget)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.runningJobFileListDock)
#         self.setDockGeometry(self.runningJobFileListDock)
        
        self.fileContentTrackerWidget = bw.FileContentTrackerWidget(self)
        self.fileContentTrackerDock = bw.createDock(
            self, 'File content tracker', self.fileContentTrackerWidget)
#         self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.fileContentTrackerDock)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.fileContentTrackerDock)
    
    #---------------------------------------------------------------------------

    def _setupConnections(self):
        
        self.centralWidget().tabWidget.currentChanged.connect(
            self._manageDockVisibility)
        
#         
#         self.runningJobFileListDock.visibilityChanged.connect(
#             lambda: self._setDockGeometry(self.runningJobFileListDock))
#         self.fileContentTrackerDock.visibilityChanged.connect(
#             lambda: self._setDockGeometry(self.fileContentTrackerDock))
    
    #---------------------------------------------------------------------------
    
    def _manageDockVisibility(self):
        
        if self.centralWidget().tabWidget.currentIndex() == 0:
            
            self.runningJobFileListDock.show()
            self.fileContentTrackerDock.show()
        else:
            self.runningJobFileListDock.hide()
            self.fileContentTrackerDock.hide()
        
    #--------------------------------------------------------------------------

    def setDockGeometry(self, dock):
        
        dock.resize(
            dock.widget().WIDTH, dock.widget().HEIGHT)
        dock.move(
            QtGui.QApplication.desktop().screen().rect().center()- self.rect().center())
        
    #--------------------------------------------------------------------------

    def showStatusMessage(self, message):

        self.statusBar().showMessage(message, self.STATUSBAR_MESSAGE_DURATION)

    #--------------------------------------------------------------------------

    def _setupActions(self):

        self.importAction = QtGui.QAction('&Import material', self)
        self.importAction.setShortcut('Ctrl+I')
        self.importAction.setIcon(
            QtGui.QIcon(os.path.join(utils.PATH_ICONS, 'document-new.png')))
        self.openAction = QtGui.QAction('&Open user DB', self)
        self.openAction.setShortcut('Ctrl+O')
        self.openAction.setIcon(
            QtGui.QIcon(os.path.join(utils.PATH_ICONS, 'document-open.png')))
        self.saveAction = QtGui.QAction('&Save changes to global DB', self)
        self.saveAction.setShortcut('Ctrl+S')
        self.saveAction.setIcon(
            QtGui.QIcon(os.path.join(utils.PATH_ICONS, 'document-save.png')))
        self.saveAsAction = QtGui.QAction('Save user DB as', self)
        self.saveAsAction.setIcon(
            QtGui.QIcon(os.path.join(utils.PATH_ICONS, 'document-save-as.png')))
        
        
        
        self.exportAction = QtGui.QAction('&Export', self)
        self.exportAction.setShortcut('Ctrl+E')
        self.exportAction.setIcon(
            QtGui.QIcon(os.path.join(utils.PATH_ICONS, 'download.png')))
        self.exitAction = QtGui.QAction('&Quit', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.aboutAction = QtGui.QAction('&About', self)
        self.aboutAction.setShortcut('Ctrl+H')
        self.showDocumentationAction = QtGui.QAction('&Documentation', self)
        self.showDocumentationAction.setShortcut('Ctrl+D')
                
        self.insertAnalyticalModelAction = QtGui.QAction('Insert Analytical Model', self)
        self.insertAnalyticalModelAction.setIcon(
            QtGui.QIcon(os.path.join(utils.PATH_ICONS, 'formula.png')))
        
        self.modifyDbTreeStructureAction = QtGui.QAction('Modify DB tree structure', self)
        self.modifyDbTreeStructureAction.setIcon(
            QtGui.QIcon(os.path.join(utils.PATH_ICONS, 'view-web-browser-dom-tree.png')))
        
#         self.showMeshLineCoastAction = QtGui.QAction('Show Mesh Line &Coast', self, checkable=True)
#         self.showMeshLineCoastAction.setShortcut('Ctrl+C')
#         self.showMeshLineDriveAction = QtGui.QAction('Show Mesh Line &Drive', self, checkable=True)
#         self.showMeshLineDriveAction.setShortcut('Ctrl+D')
# 
#         self.autoShowMeshLinesAction = QtGui.QAction('Auto-Show &Mesh Lines', self, checkable=True)
#         self.autoShowMeshLinesAction.setShortcut('Ctrl+M')
# 
#         self.showLegendAction = QtGui.QAction('Show Legend', self, checkable=True)
#         self.viewFixedAction = QtGui.QAction('&Fixed View', self, checkable=True)
#         self.viewFixedAction.setShortcut('Ctrl+F')

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(self.importAction)
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.saveAsAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exportAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAction)
        
        toolsMenu = menuBar.addMenu('&Tools')
#         unitSystemMenu = toolsMenu.addMenu('Unit system')
#         
#         self.unitSystemActions = list()
#         for unitSystemName in ei.UNIT_SYSTEMS:
#             currentUSAction = QtGui.QAction(unitSystemName, self)
#             currentUSAction.setCheckable(True)
#             self.unitSystemActions.append(currentUSAction)
#             unitSystemMenu.addAction(currentUSAction)
        toolsMenu.addAction(self.insertAnalyticalModelAction)
        
        
        viewMenu = menuBar.addMenu('&View')
        viewMenu.addAction(self.modifyDbTreeStructureAction)
        
        
#         viewMenu = menuBar.addMenu('&View')
#         viewMenu.addAction(self.showMeshLineCoastAction)
#         viewMenu.addAction(self.showMeshLineDriveAction)
#         viewMenu.addAction(self.autoShowMeshLinesAction)
#         viewMenu.addAction(self.showLegendAction)
#         viewMenu.addAction(self.viewFixedAction)

        helpMenu = menuBar.addMenu('&Help')
        helpMenu.addAction(self.aboutAction)
        helpMenu.addAction(self.showDocumentationAction)

        toolbar = self.addToolBar('File toolbar')
        toolbar.addAction(self.importAction)
        toolbar.addAction(self.openAction)
        toolbar.addAction(self.saveAction)
        toolbar.addAction(self.saveAsAction)
        toolbar.addSeparator()
        toolbar.addAction(self.exportAction)
        
        viewToolBar = self.addToolBar('View toolbar')
        viewToolBar.addAction(self.modifyDbTreeStructureAction)
        
#         self.toolsToolbar = bw.ToolsToolbar(self)
#         self.addToolBar(self.toolsToolbar)
              
    #--------------------------------------------------------------------------

    #def closeEvent(self, event):
        
        #self.parentApplication.saveSettings()
        
        #event.accept()
        
#==============================================================================
    
class Qaba(object):
    
    APPLICATION_NAME = 'qaba application'
    
    def __init__(self, args):
        
        self.args = args
        self.jobs = list()
        
        if DEBUG:
            level = logging.DEBUG
        else:
            level = logging.INFO
        utils.initiateLogging(self, level)
                
        self.setWorkDir(os.getcwd())
                                
        # initiate resource status
        ci.Resources.initialise()
        
        # check input interface
        paramProvided = self._checkInputArgs()
        if paramProvided:
            self.setupFromParameters()
        else:
            self.profile = self.setProfile()
            self.profile.runDataSelectionSequence()       
                
        for inpFileName in self.profile.inpFileNames:
            newJob = self.profile.job.getCopy()
            newJob.setInpFile(inpFileName, self.profile)
            newJob.setExecutableFile(newJob.EXECUTABLE_FILE_TYPE(self, newJob))
            newJob.executableFile.save()
            self.jobs.append(object)
            
            logging.debug(newJob.executableFile.getContent())
            logging.debug('qsub %s' % newJob.executableFile.outputFileName)
            if not DEBUG:
                utils.runSubprocess(
                    'qsub %s' % newJob.executableFile.outputFileName,
                    cwd = newJob.inpFile.dirName)         

    #--------------------------------------------------------------------------
    
    def setProfile(self):
        
        profileSelector = pi.AbaqusExecutionProfileSelector(self)
        profileType = profileSelector.getSelection()
        
        return profileType(self)
    
    #---------------------------------------------------------------------------
    
    def setWorkDir(self, path):
        
        self.workDir = path
        
        checkProjectPath(path)

    #---------------------------------------------------------------------------
        
    def getWorkDir(self):
        return self.workDir
    
    #--------------------------------------------------------------------------
    
    def _checkInputArgs(self):
        
        if self.args.inpFilePath is None:
            logging.debug('No input file parameter provided. Switching to interactive interface.')
            return False
        else:
            return True
            
    #--------------------------------------------------------------------------
    
    def setupFromParameters(self):
        
        self.profile = pi.BaseExecutionProfileType(self)
        
        # set input file
        fileNames = [os.path.abspath(fileName) for fileName in self.args.inpFilePath]
        self.profile._setInputFile(fileNames)
        
        # set license server
        licenseServerNames = [licenseServer.NAME for licenseServer in bi.LICENSE_SERVER_TYPES]
        licenseServer = bi.LICENSE_SERVER_TYPES[licenseServerNames.index(self.args.license)]
        self.profile.jobSettings.setLicenseServer(licenseServer)
        
        # set solver version
        self.profile.job.setSolverVersion(self.args.solver)
        
        # set execution server
        executionServerName = self.args.host + '.cax.lan'
        executionServer = ci.Resources.executionServers[executionServerName]
        self.profile.jobSettings.setExecutionServer(executionServer)
        
        # set job parameters
        self.profile.job.setDescription(self.args.des)
        self.profile.job.setStartTime(self.args.start)
        self.profile.job.setNumberOfCores(self.args.cpu)
        self.profile.job.setNumberOfGPUCores(self.args.gpu)
        self.profile.job.setPriority(self.args.prio)
        self.profile.jobSettings.setAdditionalSolverParams(self.args.param)

#==============================================================================
    
class Qpam(Qaba):
    
    APPLICATION_NAME = 'qpam application'
    
    def setProfile(self):
                
        profileSelector = pi.PamCrashExecutionProfileSelector(self)
        profileType = profileSelector.getSelection()
        
        return profileType(self)
    
    #--------------------------------------------------------------------------
    
    def setupFromParameters(self):
        
        self.profile = pi.PamCrashExecutionProfileType(self)
        
        # set input file
        fileNames = [os.path.abspath(fileName) for fileName in self.args.inpFilePath]
        self.profile.inpFileNames = fileNames
        self.profile.job.setInpFile(fileNames[0], self.profile)
        
        # set license server
        licenseServer = bi.PamCrashLicenseServerType
        self.profile.jobSettings.setLicenseServer(licenseServer)
        
        # set solver version
        self.profile.job.setSolverVersion(self.args.solver)
        
        # set execution server
        executionServerName = self.args.host + '.cax.lan'
        executionServer = ci.Resources.executionServers[executionServerName]
        self.profile.jobSettings.setExecutionServer(executionServer)
        
        # set job parameters
        self.profile.job.setDescription(self.args.des)
        self.profile.job.setStartTime(self.args.start)
        self.profile.job.setNumberOfCores(self.args.cpu)
        self.profile.job.setNumberOfGPUCores(self.args.gpu)
        self.profile.job.setPriority(self.args.prio)
        self.profile.jobSettings.setAdditionalSolverParams(self.args.param)

#==============================================================================
    
class Qnas(Qaba):
    
    APPLICATION_NAME = 'qnas application'
    
    def setProfile(self):
                
        profileSelector = pi.NastranExecutionProfileSelector(self)
        profileType = profileSelector.getSelection()
        
        return profileType(self)
    
    #--------------------------------------------------------------------------
    
    def setupFromParameters(self):
        
        self.profile = pi.NastranExecutionProfileType(self)
        
        # set input file
        fileNames = [os.path.abspath(fileName) for fileName in self.args.inpFilePath]
        self.profile.inpFileNames = fileNames
        self.profile.job.setInpFile(fileNames[0])
        
        # set license server
        licenseServer = bi.NastranLicenseServerType
        self.profile.jobSettings.setLicenseServer(licenseServer)
        
        # set solver version
        self.profile.job.setSolverVersion(self.args.solver)
        
        # set execution server
        executionServerName = self.args.host + '.cax.lan'
        executionServer = ci.Resources.executionServers[executionServerName]
        self.profile.jobSettings.setExecutionServer(executionServer)
        
        # set job parameters
        self.profile.job.setDescription(self.args.des)
        self.profile.job.setStartTime(self.args.start)
        self.profile.job.setNumberOfCores(self.profile.DFT_NO_OF_CORES)
        self.profile.job.setNumberOfGPUCores(0)
        self.profile.job.setPriority(self.args.prio)
        self.profile.jobSettings.setAdditionalSolverParams(self.args.param)
        
#==============================================================================

class Queue(object):
     
    APPLICATION_NAME = 'q application'
     
    def __init__(self):
         
        utils.initiateLogging(self, logging.INFO)
         
        ci.Resources.initialise()
        self.q = ci.Queue()
         
        while True:
            ci.Resources.updateState()
            os.system('clear')
            print self.q
            time.sleep(5)
        

# class Queue(QtCore.QCoreApplication):
#     
#     APPLICATION_NAME = 'q application'
#     
#     def __init__(self, args):
#         
#         super(Queue, self).__init__(args)
#         
#         utils.initiateLogging(self, logging.INFO)
#         
#         ci.Resources.initialise()
#         
#         self.q = ci.Queue()
#         self.signalGenerator = bw.SignalGenerator()
#         
#         self._setupConnections()
#         
#         self._updateQueueStatus()
#         
# #         self.setGeometry(1, 1, 1, 1)
# #         self.show()
# 
#         self.processEvents()
#         
#     #---------------------------------------------------------------------------
# 
#     def _setupConnections(self):
#         
#         self.signalGenerator.updateStatus.connect(self._updateQueueStatus)
#     
#     #---------------------------------------------------------------------------
#     
#     def _updateQueueStatus(self):
#         
#         ci.Resources.updateState()
#         os.system('clear')
#         print self.q
#     
#     #---------------------------------------------------------------------------
#     
# #     def event(self, event):
# #         
# #         print 'ewserwsf'
# #         
# #         event.accept()
#     
#     #---------------------------------------------------------------------------
#         
#     def keyPressEvent(self, event):
#         
#         print 'ewserwsf'
#         
#         if event.key() == QtCore.Qt.Key_Q:
#             print "Killing"
#             self.deleteLater()
# #         elif event.key() == QtCore.Qt.Key_Enter:
# #             self.proceed()
#         event.accept()


#==============================================================================
            
def checkProjectPath(path):
    
    for allowedPath in ei.ALLOWED_PROJECT_PATHS:
        if allowedPath in path:
            return
    
    message = 'Current path: "%s" is not valid for job submission!' % path
    message += '\nUse one of: %s' %  ei.ALLOWED_PROJECT_PATHS
    raise QabaException(message)
    
#==============================================================================

def main():

    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    args = parser.parse_args()

    try:
        app = QueueApplication(args)
        sys.exit(app.exec_())
    except Exception as e:
        logging.error(str(e))
        if DEBUG:
            traceback.print_exc()
     
        
#==============================================================================
 
if __name__ == '__main__':
    main()
    