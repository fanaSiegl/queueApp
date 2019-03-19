#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Project name
============

Project function description.

Usage
-----

project_name [input parameter]

Description
-----------

* does requires something
* does something
* creates something as an output

'''

#=========================== to be modified ===================================

APPLICATION_NAME = 'qabaPy'
DOCUMENTATON_GROUP = 'development tools'
DOCUMENTATON_DESCRIPTION = 'Python application one line description.'

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

from presentation import comp_widgets as cw
from presentation import base_widgets as bw


#==============================================================================

DEBUG = 1

#==============================================================================

class QabaException(Exception): pass

#=============================================================================

class QueueApplication(QtGui.QApplication):
    
    APPLICATION_NAME = 'queue application'
    DEBUG = DEBUG
    
    def __init__(self):
        
        super(QueueApplication, self).__init__(sys.argv)
        
        self.revision, self.modifiedBy, self.lastModified = utils.getVersionInfo()
        self.userName, self.machine, self.email = utils.getUserInfo()
        
        if DEBUG:
            level = logging.DEBUG
        else:
            level = logging.WARNING
        utils.initiateLogging(self, level)
                
        # connect resources
        bi.Resources.initialise()
        self.q = bi.Queue()       
                
        self.signalGenerator = bw.SignalGenerator()
        
        self.mainWindow = MainWindow(self)
        
        self._setupConnections()
        
        self._updateQueueStatus()
        
        self.mainWindow.show()
    
    #---------------------------------------------------------------------------

    def _setupConnections(self):
        
        self.signalGenerator.updateStatus.connect(self._updateQueueStatus)
    
    #---------------------------------------------------------------------------

    def _updateQueueStatus(self):
        
        bi.Resources.updateState()
        
        self.mainWindow.centralWidget().queueTabWidget.updateContent()
        self.mainWindow.showStatusMessage('Status updated')
    
    #---------------------------------------------------------------------------

    def showInfoMessage(self, message):
        
        self.restoreOverrideCursor()
        
        QtGui.QMessageBox.information(self.mainWindow, '%s' % self.APPLICATION_NAME,
                str(message))

#===============================================================================

class MainWindow(QtGui.QMainWindow):

    WIDTH = 1300
    HEIGHT = 700

    STATUSBAR_MESSAGE_DURATION = 2000
        
    def __init__(self, parentApplication):
        super(MainWindow, self).__init__()

        self.parentApplication = parentApplication
                        
#         self._setupActions()
        self._setupWidgets()

        self._setWindowGeometry()
    
    #---------------------------------------------------------------------------

    def _setWindowGeometry(self):
        
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
        
        utils.initiateLogging(self, logging.INFO)
        
        self.workDir = os.getcwd()
        
        checkProjectPath(self.workDir)
        
        self.jobs = list()
        
        # initiate resource status
        bi.Resources.initialise()
#         bi.BaseExecutionServerType.connectResources2()
                
        self.profile = self.setProfile()
        self.profile.runDataSelectionSequence()       
                
        for inpFileName in self.profile.inpFileNames:
            newJob = self.profile.job.getCopy()
            newJob.setInpFile(inpFileName)
            newJob.setExecutableFile(newJob.EXECUTABLE_FILE_TYPE(self, newJob))
            newJob.executableFile.save()
            self.jobs.append(object)
        
        if DEBUG:
            print 'qsub %s' % newJob.executableFile.outputFileName
        else:
            utils.runSubprocess('qsub %s' % newJob.executableFile.outputFileName)

    #--------------------------------------------------------------------------
    
    def setProfile(self):
        
        profileSelector = ci.AbaqusExecutionProfileSelector(self)
        profileType = profileSelector.getSelection()
        
        return profileType(self)
    
    #---------------------------------------------------------------------------
    
    def setWorkDir(self, path):
        self.workDir = path

    #---------------------------------------------------------------------------
        
    def getWorkDir(self):
        return self.workDir

#==============================================================================
    
class Qpam(Qaba):
    
    APPLICATION_NAME = 'qpam application'
    
    def setProfile(self):
                
        profileSelector = ci.PamCrashExecutionProfileSelector(self)
        profileType = profileSelector.getSelection()
        
        return profileType(self)

#==============================================================================

class Queue(object):
    
    APPLICATION_NAME = 'q application'
    
    def __init__(self):
        
        utils.initiateLogging(self, logging.INFO)
        
        bi.Resources.initialise()
#         bi.BaseExecutionServerType.connectResources2()
        self.q = bi.Queue()
        
        while True:
#             bi.BaseExecutionServerType.connectResources2()
            bi.Resources.updateState()
            os.system('clear')
            print self.q
            time.sleep(5)
        

#==============================================================================
            
def checkProjectPath(path):
    
    for allowedPath in ei.ALLOWED_PROJECT_PATHS:
        if allowedPath in path:
            return
    
    message = 'Current path: "%s" is not valid for job submission!' % path
    message += '\nUse one of: %s' %  ei.ALLOWED_PROJECT_PATHS
    raise QabaException(message)
    
#==============================================================================

def getListOfHosts():
    
    # initiate resource status
    bi.Resources.initialise()
#     bi.BaseExecutionServerType.connectResources2()
    
    hosts = list()
    for licenseServer in bi.LICENSE_SERVER_TYPES:
        hosts.extend(
            [currentHost.name for currentHost in licenseServer.getAvailableHosts()])
    
    return sorted(set(hosts))

#==============================================================================

def main():

    try:
        app = QueueApplication()
        sys.exit(app.exec_())
    except Exception as e:
        print str(e)
        if DEBUG:
            traceback.print_exc()
     
        
#==============================================================================
 
if __name__ == '__main__':
    main()
    