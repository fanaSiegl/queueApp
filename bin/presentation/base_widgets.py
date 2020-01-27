#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import glob
import subprocess
from functools import partial
import xml.etree.ElementTree as ETree

from PyQt4 import QtCore, QtGui

# from domain import base_items as bi

#==============================================================================

class SignalGenerator(QtCore.QTimer):

    PERIOD = 10.0 # s
    updateStatus = QtCore.pyqtSignal()

    def __init__(self):
        super(SignalGenerator, self).__init__()

        self.timeout.connect(self.update)
        
        self.startGenerator()
        
    #---------------------------------------------------------------------------

    def update(self):
        
        self.updateStatus.emit()

    #---------------------------------------------------------------------------

    def startGenerator(self):

        self.values = list()
        self.start(self.PERIOD*1000)
        
#=============================================================================

class BaseSelectorWidget(QtGui.QWidget):
    
    changed = QtCore.pyqtSignal(object)
    
    def __init__(self, selectorItem):
        super(BaseSelectorWidget, self).__init__()
        
        self.selectorItem = selectorItem
                
        self.items = list()
        
        self.setLayout(QtGui.QVBoxLayout())
        
        self._setupWidgets()
#         self.setupOptions()
        
    #---------------------------------------------------------------------------
    
    def _getSelectorItemOptions(self):
        
        self.options = self.selectorItem.getOptions()
    
    #---------------------------------------------------------------------------
    
    def _setupWidgets(self):
        
        self.buttonLayout = QtGui.QVBoxLayout()
        self.buttonGroup = QtGui.QGroupBox(self.selectorItem.DESCRIPTION)
                
        self.buttonGroup.setLayout(self.buttonLayout)
        self.layout().addWidget(self.buttonGroup)
            
    #---------------------------------------------------------------------------
    
    def setupOptions(self):
        
        self._getSelectorItemOptions()
                
        for option in self.options:
            optionButton = QtGui.QRadioButton(str(option))
            optionButton.released.connect(self.valueChanged)
            self.buttonLayout.addWidget(optionButton)
            
            self.items.append(optionButton)
                
        self.setDefaultOption(self.selectorItem.DFT_OPTION_INDEX)
    
    #---------------------------------------------------------------------------
    
    def getSelection(self):
        
        for index, optionButton in enumerate(self.items):
            if optionButton.isChecked():
                return self.selectorItem.indexToItem(index)
        
        return None
    
    #---------------------------------------------------------------------------
    
    def valueChanged(self):
        
        self.changed.emit(self.getSelection())
    
    #---------------------------------------------------------------------------
    
    def setDefaultOption(self, index):
        
        if len(self.items) == 0:
            return
  
        defaultButton = self.items[index - 1]
        defaultButton.setChecked(True)
        
        self.valueChanged()

#=============================================================================

class ExecutionServerSelectorWidget(BaseSelectorWidget):
    
    #---------------------------------------------------------------------------
    
    def _getSelectorItemOptions(self):
        
        self.hosts, self.options, serverHosts, userHosts, self.description = self.selectorItem.getOptions()
    
    #---------------------------------------------------------------------------
    
    def _setupWidgets(self):
        
        groupLayout = QtGui.QVBoxLayout()
        group = QtGui.QGroupBox(self.selectorItem.DESCRIPTION)
        group.setLayout(groupLayout)
        
        self.listWidget = QtGui.QListWidget()
        self.infoLabel = QtGui.QLabel('')
                
        description = 'queue name                  qtype resv/used/tot. load_avg    arch       states'
        
        self.columnLabels = QtGui.QLabel(description)
        font = QtGui.QFont()
        font.setFamily("Courier New")
        self.columnLabels.setFont(font)
        
        groupLayout.addWidget(self.infoLabel)
        groupLayout.addWidget(self.columnLabels)
        groupLayout.addWidget(self.listWidget)
        self.layout().addWidget(group)
                        
        self.listWidget.currentRowChanged.connect(self.valueChanged)
            
    #---------------------------------------------------------------------------
    
    def setupOptions(self):
        
        self._getSelectorItemOptions()
        
        self.listWidget.blockSignals(True)
              
        self.listWidget.clear()
        self.items = list()
        
        self.infoLabel.setText(self.description)
        
        for optionIndex, option in enumerate(self.options):
            item = QtGui.QListWidgetItem(str(option))
            font = QtGui.QFont()
            font.setFamily("Courier New")
            item.setFont(font)
#             item.setCheckState(0)
            self.listWidget.addItem(item)
            
            if self.hosts[optionIndex].isUserMachine:
                item.setTextColor(QtGui.QColor("blue"))
                        
            self.items.append(item)
        
        self.listWidget.blockSignals(False)
#         self.setDefaultOption(self.selectorItem.DFT_OPTION_INDEX)
            
    #---------------------------------------------------------------------------
    
    def getSelection(self):
        
        index = self.listWidget.currentRow()
        
        return self.selectorItem.indexToItem(index)
    
    #---------------------------------------------------------------------------
    
    def setDefaultOption(self, index):
        
#         self.items[index - 1].setSelected(True)
        self.listWidget.setCurrentRow(index - 1)
        
#         self.valueChanged()

    #---------------------------------------------------------------------------
    
    def setEnabled(self, value):
        
        self.listWidget.setEnabled(value)
        
#=============================================================================

class WorkingDirectorySelectorWidget(QtGui.QWidget):
    
    changed = QtCore.pyqtSignal(object)
    
    def __init__(self, selectorItem):
        super(WorkingDirectorySelectorWidget, self).__init__()
        
        self.selectorItem = selectorItem
        
        self.setLayout(QtGui.QHBoxLayout())
        
#         groupLayout = QtGui.QHBoxLayout()
#         group = QtGui.QGroupBox('Select working directory')
#         group.setLayout(groupLayout)
        
        self.lineEdit = QtGui.QLineEdit()
        self.openButton = QtGui.QPushButton('Browse') 
        
        self.layout().addWidget(QtGui.QLabel('Select working directory'))
        self.layout().addWidget(self.lineEdit)
        self.layout().addWidget(self.openButton)
#         self.layout().addWidget(group)
        
        self.openButton.released.connect(self.openFile)
        
    #---------------------------------------------------------------------------

    def openFile(self):
        
        workDir = self.selectorItem.parentApplication.getWorkDir()
        
        projectDir = QtGui.QFileDialog.getExistingDirectory(
            self, 'Select working directory', workDir)
        
        if projectDir:
            self.changed.emit(str(projectDir))
        
#         
#         fileNames = QtGui.QFileDialog.getOpenFileNames(self,
#             'Open *%s file' % self.selectorItem.FILE_EXT, workDir,
#             'Input files (*%s)' % self.selectorItem.FILE_EXT)
#         
#         if fileNames:
#             fileNames = [str(fileName) for fileName in fileNames]
#             self.lineEdit.setText(', '.join(fileNames))
#             
#             self.changed.emit(fileNames)
            
        
#=============================================================================

class InputFileSelectorWidget(QtGui.QWidget):
    
    changed = QtCore.pyqtSignal(object)
    
    def __init__(self, selectorItem):
        super(InputFileSelectorWidget, self).__init__()
        
        self.selectorItem = selectorItem
        
        self._setupWidgets()
        self._setupConnections()
    
    #---------------------------------------------------------------------------
    
    def _setupWidgets(self):
        
        self.setLayout(QtGui.QVBoxLayout())
        
        groupLayout = QtGui.QVBoxLayout()
        group = QtGui.QGroupBox('Select input file(s)')
        group.setLayout(groupLayout)
        
        self.workingDirectorySelectorWidget = WorkingDirectorySelectorWidget(self.selectorItem)
        
        self.view = InputFilesTreeView(self.selectorItem)
        
        groupLayout.addWidget(self.workingDirectorySelectorWidget)
        groupLayout.addWidget(self.view)
        
        self.layout().addWidget(group)


    #---------------------------------------------------------------------------
    
    def _setupConnections(self):
        
        self.view.itemSelectionChanged.connect(self.valueChanged)
        
        self.workingDirectorySelectorWidget.changed.connect(self.findInputFiles)
        
    #---------------------------------------------------------------------------

    def setupInputFiles(self):
                        
        options = self.selectorItem.getOptions()
        
        if len(options) == 1:
            firstIndexPath = os.path.join(str(self.view.model().rootPath()), options[0])
            firstIndex = self.view.model().index(firstIndexPath)
            self.view.setCurrentIndex(firstIndex)
            
            self.valueChanged()
                
    #---------------------------------------------------------------------------
    
    def getSelection(self):
                        
        return self.view.getSelectedItems()
    
    #---------------------------------------------------------------------------
    
    def valueChanged(self):
        
        selectedFilesNames = list()
        for selectedItem in self.getSelection():
            if os.path.isfile(selectedItem):
                selectedFilesNames.append(selectedItem)
        
#         if len(selectedFilesNames) > 0:
        self.changed.emit(selectedFilesNames)
    
    #--------------------------------------------------------------------------

    def findInputFiles(self, projectDir):

        self.selectorItem.parentApplication.setWorkDir(projectDir)
        
        self.workingDirectorySelectorWidget.lineEdit.setText(projectDir)
        
        self.view.setRootIndex(self.view.model().setRootPath(projectDir))        
        self.setupInputFiles()

#=============================================================================

class BaseIntSelectorWidget(QtGui.QWidget):
    
    changed = QtCore.pyqtSignal(object)
    
#     GROUP_LABEL = ''
    LABEL = ''
    
    def __init__(self):
        super(BaseIntSelectorWidget, self).__init__()
                
        self._setupWidgets()
        self._setupConnections()
    
    #---------------------------------------------------------------------------
    
    def _setupWidgets(self):
        
        self.setLayout(QtGui.QHBoxLayout())
        
#         groupLayout = QtGui.QHBoxLayout()
#         group = QtGui.QGroupBox(self.GROUP_LABEL)
#         group.setLayout(groupLayout)
        
        self.spinBox = QtGui.QSpinBox()
                
#         groupLayout.addWidget(QtGui.QLabel(self.LABEL))
#         groupLayout.addWidget(self.spinBox)
#         self.layout().addWidget(group)
        
        self.layout().addWidget(QtGui.QLabel(self.LABEL))
        self.layout().addWidget(self.spinBox)
        
    #---------------------------------------------------------------------------
    
    def _setupConnections(self):
        
        self.spinBox.valueChanged.connect(self.valueChanged)
    
    #---------------------------------------------------------------------------
    
    def setDefaultOption(self, minValue, maxValue, dftValue):
        
        self.spinBox.setMinimum(minValue)
        self.spinBox.setMaximum(maxValue)
        self.spinBox.setValue(dftValue)
    
    #---------------------------------------------------------------------------
    
    def valueChanged(self):
        
        self.changed.emit(self.spinBox.value())

#=============================================================================

class NoOfCoresSelectorWidget(BaseIntSelectorWidget):
    
#     GROUP_LABEL = 'Choose the number of CPUs'
    LABEL = 'Enter number of CPU cores'

#=============================================================================

class NoOfGpusSelectorWidget(BaseIntSelectorWidget):
    
#     GROUP_LABEL = 'Choose the number of GPUs'
    LABEL = 'Enter number of NVIDIA GPU acceleration'
    
    #---------------------------------------------------------------------------
    
    def setDefaultOption(self, minValue, maxValue, dftValue):
        super(NoOfGpusSelectorWidget, self).setDefaultOption(minValue, maxValue, dftValue)
        
        if maxValue == 0:
            self.setEnabled(False)
        else:
            self.setEnabled(True)
        
#=============================================================================

class JobPrioritySelectorWidget(BaseIntSelectorWidget):
    
    GROUP_LABEL = 'Choose job priority'
    LABEL = 'Enter priority in the queue'    

#=============================================================================

class BaseLineEditWidget(QtGui.QWidget):
    
    changed = QtCore.pyqtSignal(object)
    
    LABEL = ''
    
    def __init__(self):
        super(BaseLineEditWidget, self).__init__()
                
        self._setupWidgets()
        self._setupConnections()
    
    #---------------------------------------------------------------------------
    
    def _setupWidgets(self):
        
        self.setLayout(QtGui.QHBoxLayout())
                
        self.lineEdit = QtGui.QLineEdit()
          
        self.layout().addWidget(QtGui.QLabel(self.LABEL))
        self.layout().addWidget(self.lineEdit)
        
    #---------------------------------------------------------------------------
    
    def _setupConnections(self):
        
        self.lineEdit.textChanged.connect(self.valueChanged)
        
    #---------------------------------------------------------------------------
    
    def valueChanged(self):
        
        self.changed.emit(self.lineEdit.text())
    
    #---------------------------------------------------------------------------
    
    def setDefaultOption(self, text):
        
        self.lineEdit.setText(text)
    

#=============================================================================

class JobDescriptionSelectorWidget(BaseLineEditWidget):
    
    LABEL = 'Enter description of job (15 characters)' 

#=============================================================================

class SolverParametersSelectorWidget(BaseLineEditWidget):
    
    LABEL = 'Specify more job parameters (15 characters)' 

#=============================================================================

class JobStartTimeSelectorWidget(QtGui.QWidget):
    
    changed = QtCore.pyqtSignal(object)
    
    LABEL = 'Enter deferred time of computation'
    
    def __init__(self):
        super(JobStartTimeSelectorWidget, self).__init__()
                
        self._setupWidgets()
        self._setupConnections()
    
    #---------------------------------------------------------------------------
    
    def _setupWidgets(self):
        
        self.setLayout(QtGui.QHBoxLayout())
        
#         self.caledarWidget = QtGui.QCalendarWidget(self)
        
        self.dateTimeEdit = QtGui.QDateTimeEdit(QtCore.QDateTime.currentDateTime())
        self.dateTimeEdit.setDisplayFormat("hh:mm dd/MM/yyyy")
#         self.dateTimeEdit.setCalendarPopup(True)
#         self.dateTimeEdit.setCalendarWidget(self.caledarWidget)
        
        self.layout().addWidget(QtGui.QLabel(self.LABEL))
        self.layout().addWidget(self.dateTimeEdit)
        
    #---------------------------------------------------------------------------
    
    def _setupConnections(self):
        
        self.dateTimeEdit.dateTimeChanged.connect(self.valueChanged)
        
    #---------------------------------------------------------------------------
    
    def valueChanged(self):
        
        timeString = self.dateTimeEdit.dateTime().toString('MMddhhmm')
        
        self.changed.emit(timeString)
            
#===============================================================================

class BaseListWidget(QtGui.QListWidget):
    
    itemNameChanged = QtCore.pyqtSignal(list)
    
    def __init__(self, parentWidget):
        
        super(BaseListWidget, self).__init__()
        
        self.parentWidget = parentWidget
        self.parentApplication = parentWidget.parentApplication
        
        self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        
        self.itemSelectionChanged.connect(self.itemSelected)
#         self.itemChanged.connect(self.itemRenamed)
    
        self.doubleClicked.connect(self.itemDoubleClicked)
    
    #--------------------------------------------------------------------------

    def itemRenamed(self, editedItem):
        
        editedItem.dataItem.setAttribute('NAME', unicode(editedItem.text()))
        
        self.itemNameChanged.emit([editedItem.dataItem])
    
    #--------------------------------------------------------------------------

    def itemDoubleClicked(self): pass
    
    #--------------------------------------------------------------------------

    def itemSelected(self): pass
    
    #--------------------------------------------------------------------------

    def contextMenuEvent(self, event):
        
        index = self.indexAt(event.pos())
        
        if index.isValid():
#             item = self.model().itemFromIndex(index)
#             item.openContextMenu(self)
            
            point = self.mapFromGlobal(QtGui.QCursor.pos())
            itemUnderCursor = self.itemAt(point)
            if itemUnderCursor is not None:
                itemUnderCursor.openContextMenu(self)
        else:
            self.openContextMenu()
        
#         # prevent opening a wrong context menu
#         point = self.mapFromGlobal(QtGui.QCursor.pos())
#         itemUnderCursor = self.itemAt(point)
#         if itemUnderCursor is not None:
#             itemUnderCursor.openContextMenu(self)
#         else:
#             self.openContextMenu()
        
        #self.currentItem().openContextMenu(self)
    
    #--------------------------------------------------------------------------

    def openContextMenu(self):
        
        pass

#===============================================================================

class QueueListWidget(BaseListWidget):
    
    itemForTrackingSelected = QtCore.pyqtSignal(object)
    
    def itemSelected(self):
        
        selectedItems = list()
        for item in self.selectedItems():
            if item.dataItem is not None:
                selectedItems.append(item.dataItem)
        
        
#         if len(selectedItems) > 0:
#             self.parentApplication.signalController.materialImporterItemsSelected.emit(selectedItems)
    

#===============================================================================

class RunningJobFileListWidget(BaseListWidget):
    
    WIDTH = 400
    HEIGHT = 600
    
    itemForTrackingSelected = QtCore.pyqtSignal(object, str)
    
    #------------------------------------------------------------------------------ 
    
    def setupContent(self, dataItem):
        
        fileNames = dataItem.getListOfFiles()
        
        self.clear()
        
        for fileName in fileNames:
            newItem = RunningJobFileListWidgetItem(dataItem, fileName)
            
            self.addItem(newItem)
    
    #--------------------------------------------------------------------------

    def itemDoubleClicked(self):
        
        for item in self.selectedItems():
            if item.dataItem is not None:
                item.trackContent(self)       
    
    
#=============================================================================

class BaseListWidgetItem(QtGui.QListWidgetItem):
    
#     ICON_PATH = os.path.join(utils.PATH_ICONS, 'mail-tagged.png')
    
    def __init__(self, dataItem):
        
        self.dataItem = dataItem
        
        super(BaseListWidgetItem, self).__init__(self.dataItem.toString(colour=False))
        
#         self.setIcon(QtGui.QIcon(self.ICON_PATH))
        self.setToolTip(self.dataItem.getTooltip())
        #self.setEditable(True)
#         self.setFlags(self.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable)
#         self.setCheckState(QtCore.Qt.Unchecked)
#         setFlags (item->flags () & Qt::ItemIsEditable)
        
        font = QtGui.QFont()
        font.setFamily("Courier New")
        self.setFont(font)
        
    #------------------------------------------------------------------------------ 
    
    def openContextMenu(self, parentWidget):
        
        pass

#=============================================================================

# class QueueJobListWidgetItem(BaseListWidgetItem):
#     
#     def __init__(self, dataItem):
#         super(QueueJobListWidgetItem, self).__init__(dataItem)
#         
#         
#         if 'abaqus' in self.dataItem.licenceServer.CODE:
#             self.setTextColor(QtGui.QColor("blue"))
#         elif 'pamcrash' in self.dataItem.licenceServer.CODE:
#             self.setTextColor(QtGui.QColor("green"))
#         
#         if self.dataItem.isOutOfTheQueue:
#             self.setTextColor(QtGui.QColor("red"))
#             
#     #------------------------------------------------------------------------------ 
#     
#     def openContextMenu(self, parentWidget):
#         
#         menu = QtGui.QMenu()
#         
#         jobInfoAction = menu.addAction('Job info')
#         jobContentAction = menu.addAction('Check progress')
#         jobKillAction = menu.addAction('Terminate')
#         
#         jobInfoAction.triggered.connect(self.jobInfo)
#         jobContentAction.triggered.connect(
#             lambda: self.showContent(parentWidget))
#         jobKillAction.triggered.connect(self.jobTerminate)
#         
#         # check autority
# #         if parentWidget.parentApplication.userName != self.dataItem['JB_owner']:
# #             jobKillAction.setEnabled(False)
#         if self.dataItem.isOutOfTheQueue:
#             jobKillAction.setEnabled(False)
#         
#         if self.dataItem.isOutOfTheQueue:
#             jobContentAction.setEnabled(False)
#         elif self.dataItem._attributes['state'] != 'r':
#             jobContentAction.setEnabled(False)
#                     
#         menu.exec_(QtGui.QCursor.pos())
#     
#     #------------------------------------------------------------------------------ 
#     
#     def jobTerminate(self):
#         
#         quitMsg = "Are you sure to terminate the job?"
#         reply = QtGui.QMessageBox.question(None, 'Exit', 
#             quitMsg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
#     
#         if reply == QtGui.QMessageBox.Yes:
#             status = self.dataItem.terminate()
#         
#             QtGui.QMessageBox.information(None, 'Terminate job %s info' % self.dataItem.id,
#                     str(status))
    
    #------------------------------------------------------------------------------ 
    
    def jobInfo(self):
        
        QtGui.QMessageBox.information(None, 'Job %s info' % self.dataItem.id,
                str(self.dataItem.getInfo()))
        
    #------------------------------------------------------------------------------ 
    
    def showContent(self, parentWidget):
        
        parentWidget.itemForTrackingSelected.emit(self.dataItem)
        

#=============================================================================

class RunningJobFileListWidgetItem(QtGui.QListWidgetItem):
        
    def __init__(self, dataItem, parentFileName):
        
        self.parentFileName = parentFileName
        self.dataItem = dataItem
        
        super(RunningJobFileListWidgetItem, self).__init__(
            parentFileName)
        
        self.setToolTip(self.dataItem.getTooltip())
        
#         self.setFlags(self.flags() | QtCore.Qt.ItemIsUserCheckable)
#         self.setCheckState(QtCore.Qt.Unchecked)
        
#         
#         font = QtGui.QFont()
#         font.setFamily("Courier New")
#         self.setFont(font)   
            
    #------------------------------------------------------------------------------ 
    
    def openContextMenu(self, parentWidget):
        
        menu = QtGui.QMenu()
        
        trackChangesAction = menu.addAction('Track content changes')
        trackChangesAction.triggered.connect(
            lambda: self.trackContent(parentWidget))
                    
        menu.exec_(QtGui.QCursor.pos())
    
    #------------------------------------------------------------------------------ 
    
    def trackContent(self, parentWidget):
        
        parentWidget.itemForTrackingSelected.emit(self.dataItem, self.parentFileName)
        
#=============================================================================

class FileContentTrackerWidget(QtGui.QTabWidget):
    
    WIDTH = 800
    HEIGHT = 600
    
    def __init__(self, mainWindow):
        super(FileContentTrackerWidget, self).__init__(mainWindow)
        
        self.mainWindow = mainWindow
        self.parentApplication = mainWindow.parentApplication
            
    #------------------------------------------------------------------------------ 
    
    def setupContent(self, jobItem, fileName):
        
        name = '%s (Job: %s)' %(fileName, jobItem.id)
        trackedFileContentWidget = TrackedFileContentWidget(self, jobItem, fileName)
        tabIndex = self.addTab(trackedFileContentWidget, name)
        
        button = QtGui.QPushButton('x')
        button.released.connect(
            partial(self.removeTracking, trackedFileContentWidget))
        
        self.tabBar().setTabButton(tabIndex, QtGui.QTabBar.RightSide, button)
        
    #------------------------------------------------------------------------------ 
    
    def removeTracking(self, tabWidget):
                
        tabWidget.stopTracking()
        
        self.removeTab(self.indexOf(tabWidget))
        
        
        
#         tempSepAction.triggered.connect(
#                 #lambda: self.separateMaterial(parentWidget, stateVariable))
#                 partial(self.separateMaterial, parentWidget, stateVariable))

#=============================================================================

class TrackedFileContentWidget(QtGui.QWidget):
    
    def __init__(self, parentWidget, dataItem, fileName):
        super(TrackedFileContentWidget, self).__init__(parentWidget)
        
        self.parentWidget = parentWidget
        self.parentApplication = parentWidget.parentApplication
        self.dataItem = dataItem
        self.fileName = fileName
        
        self.setLayout(QtGui.QVBoxLayout())
        
        self.fileContentTextEdit = QtGui.QTextEdit()
        self.fileContentTextEdit.setReadOnly(True)
        font = QtGui.QFont()
        font.setFamily("Courier New")
        self.fileContentTextEdit.setFont(font)   
        
        self.layout().addWidget(self.fileContentTextEdit)
                
        self.fileContentTrackerThread = FileContentTrackerThread(self)
        self.fileContentTrackerThread.contentUpdated.connect(
            self._updateContent)
        self.parentApplication.signalGenerator.updateStatus.connect(
            self.fileContentTrackerThread.start)
        
        # initiate content
        self._updateContent(self.dataItem.getTrackedFileContent(self.fileName))
        
    #------------------------------------------------------------------------------ 
    
    def _updateContent(self, trackedFileContent):
        
        self.fileContentTextEdit.clear()
        
        self.fileContentTextEdit.setText(trackedFileContent)
        self.fileContentTextEdit.moveCursor(QtGui.QTextCursor.End)
        
    #------------------------------------------------------------------------------ 
    
    def stopTracking(self):
        
        self.parentApplication.signalGenerator.updateStatus.disconnect(
            self.fileContentTrackerThread.start)

#==============================================================================

class FileContentTrackerThread(QtCore.QThread):
    
    contentUpdated = QtCore.pyqtSignal(str)
    
    def __init__(self, parentWidget):
        super(FileContentTrackerThread, self).__init__()
        
        self.parentWidget = parentWidget
        self.parentApplication = parentWidget.parentApplication
        self.dataItem = self.parentWidget.dataItem
        self.fileName = self.parentWidget.fileName
                
        self.fileContent = ''
        
    #--------------------------------------------------------------------------
    
    def run(self):
        
        content = self.dataItem.getTrackedFileContent(self.fileName)
        
        if content != self.fileContent:
            self.fileContent = content        
            self.contentUpdated.emit(self.fileContent)
    
    #--------------------------------------------------------------------------


#===============================================================================

class InputFilesTreeView(QtGui.QTreeView):
    
    headerColumnVisibilityChanged = QtCore.pyqtSignal(list)
    TAG = 'InputFilesTreeView'
    itemSelectionChanged = QtCore.pyqtSignal(list)
    
    def __init__(self, selectorItem):
        
        super(InputFilesTreeView, self).__init__()
        
        self.selectorItem = selectorItem
        self.parentApplication = self.selectorItem.parentApplication
        
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
                
        self.fileSystemModel = QtGui.QFileSystemModel()
        self.fileSystemModel.setNameFilters(QtCore.QStringList('*' + self.selectorItem.FILE_EXT))
        self.fileSystemModel.setNameFilterDisables(False)
        
#         self.fileSystemModel.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.Files )
        
        self.setModel(self.fileSystemModel)
#         self.setRootIsDecorated(False)
        
        self.expandAll()
        self.setSortingEnabled(True)
        self.sortByColumn(0, QtCore.Qt.AscendingOrder)
#         self.view.resizeColumnToContents(0)
        self.setColumnWidth(0, 400)
        
    #--------------------------------------------------------------------------

    def getSelectedItems(self):
         
        selectedItems = list()
        for index in self.selectedIndexes():
            path = index.model().filePath(index)
            
            if index.column() > 0:
                continue
            selectedItems.append(str(path))
         
        return selectedItems
     
    #--------------------------------------------------------------------------
    
    def mouseReleaseEvent(self, event):
        
        super(InputFilesTreeView, self).mouseReleaseEvent(event)
        
        self.itemSelected(self.currentIndex())
    
    #--------------------------------------------------------------------------

    def itemSelected(self, index):
        
        selectedItems = list()
        for index in self.selectedIndexes():
            path = index.model().filePath(index)
            
            if index.column() > 0:
                continue
            selectedItems.append(str(path))
        
        self.itemSelectionChanged.emit(selectedItems)
                
#===============================================================================

class QueueTreeView(QtGui.QTreeView):
    
    headerColumnVisibilityChanged = QtCore.pyqtSignal(list)
    itemForTrackingSelected = QtCore.pyqtSignal(object)
        
    TAG = 'QueueTreeView'
    DFT_ATTRIBUTES_VISIBILITY = [
        'job_number', 'priority', 'JB_owner', 'JB_name', 'state',
        'JAT_start_time', 'queue_name_hr', 'hard_request']
    
    def __init__(self, parentWidget):
        
        super(QueueTreeView, self).__init__()
        
        self.parentWidget = parentWidget
        self.parentApplication = self.parentWidget.parentApplication
        self.queue = self.parentWidget.queue
        
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.setSortingEnabled(True)
        self.setRootIsDecorated(False)
        
        self.activated.connect(self.itemSelected)
        self.doubleClicked.connect(self.itemDoubleClicked)
        #self.selectionChanged()
        #self.header().hide()
        
#         self.setModel(self.application.contentProvider.getDatabaseModel())
        headerView = self.header()
        headerView.setClickable(True)
        headerView.sectionClicked.connect(self.showHeaderColumnOptions)
        
        self.headerColumnVisibility = list()
                
    #--------------------------------------------------------------------------

    def contextMenuEvent(self, event):
                        
        index = self.indexAt(event.pos())
        
        if index.isValid():
            item = self.model().itemFromIndex(index)
            item.openContextMenu(self)
        else:
            self.openContextMenu()
        
#         if len(self.selectedIndexes()) > 0:
#             item = self.model().itemFromIndex(self.selectedIndexes()[0])
#             item.openContextMenu(self)
#         else:
#             self.openContextMenu()
            
    #--------------------------------------------------------------------------

    def openContextMenu(self):
        
        return
        menu = QtGui.QMenu()
                
        modifyTreeStructureAction = menu.addAction('Modify DB tree structure')
#         modifyTreeStructureAction.setIcon(
#             QtGui.QIcon(os.path.join(utils.PATH_ICONS, 'view-web-browser-dom-tree.png')))
        modifyTreeStructureAction.triggered.connect(
            self.parentApplication.showDatabaseTreeStructureDialog)
        
        importMaterialAction = menu.addAction('Import material')
#         importMaterialAction.setIcon(
#             QtGui.QIcon(os.path.join(utils.PATH_ICONS, 'document-new.png')))
        importMaterialAction.triggered.connect(
            self.parentApplication.showMaterialImportDialog)
        
        menu.exec_(QtGui.QCursor.pos())
    
    #--------------------------------------------------------------------------

#     def getSelectedItems(self):
#         
#         selectedItems = list()
#         for index in self.selectedIndexes():
#             item = index.model().itemFromIndex(index)
#             if index.column() > 0:
#                 continue
#             if item.dataItem is not None:
#                 selectedItems.append(item.dataItem)
#         
#         return selectedItems
     
    #--------------------------------------------------------------------------

    def itemSelected(self, index):
        
        selectedItems = list()
        selectedRows = list()
        for index in self.selectedIndexes():
            item = index.model().itemFromIndex(index)
            currentRow = item.row()
            if currentRow not in selectedRows:
                selectedRows.append(currentRow)
            else:
                continue
            if item.dataItem is not None:
                selectedItems.append(item.dataItem)
        
        if len(selectedItems) > 0:
#             print selectedItems
            pass
#             self.parentApplication.signalController.navigationItemsSelected.emit(selectedItems)
    
    #------------------------------------------------------------------------------ 
    
    def itemDoubleClicked(self):
        
        selectedItems = list()
        selectedRows = list()
        for index in self.selectedIndexes():
            item = index.model().itemFromIndex(index)
            currentRow = item.row()
            if currentRow not in selectedRows:
                selectedRows.append(currentRow)
            else:
                continue
            if item.dataItem is not None:
                selectedItems.append(item.dataItem)
        
#         if len(selectedItems) > 0:
        for selectedItem in selectedItems:
            self.itemForTrackingSelected.emit(selectedItem)
#             self.parentApplication.signalController.navigationItemsDoubleClicked.emit(selectedItems)
        
    #------------------------------------------------------------------------------ 
    
    def _getAllIndexes(self):
        
        return self.model().match(
            self.model().index(0,0), QtCore.Qt.DisplayRole, '*',
            hits=-1, flags=QtCore.Qt.MatchWildcard|QtCore.Qt.MatchRecursive)
    
    #------------------------------------------------------------------------------ 
    
    def expandFirstChildren(self):
        
#         rootIndex = self.model().index(0,0)
#         rootItem = self.model().itemFromIndex(rootIndex)
#         
#         print self.model().rowCount()
        for row in range(self.model().rowCount()):
            self.expand(self.model().index(row, 0))
            
    #--------------------------------------------------------------------------

    def updateViewHeader(self):
        
        # if column visibility has been already defined
        if len(self.headerColumnVisibility) > 0:
            return
                
#         self.headerColumnVisibility.append(True)
        visibleColumns = dict()
        for i in range(self.header().count()-1):
            if str(self.model().headerLabels[i]) in self.DFT_ATTRIBUTES_VISIBILITY:
                isVisible = True
                visibleColumns[str(self.model().headerLabels[i])] = i
#                 headerView = self.header()
#                 headerView.moveSection(
#                     i, self.DFT_ATTRIBUTES_VISIBILITY.index(str(self.model().headerLabels[i])))
#                 print i, self.DFT_ATTRIBUTES_VISIBILITY.index(str(self.model().headerLabels[i]))
            else:
                isVisible = False
            self.headerColumnVisibility.append(isVisible)
            self.setColumnVisible(i, isVisible)           
        
        # sort columns
        headerView = self.header()
        for visibleAttrName in self.DFT_ATTRIBUTES_VISIBILITY[::-1]:
            currentVisibilityIndex = headerView.visualIndex(visibleColumns[visibleAttrName])
            targetVisibilityIndex = self.DFT_ATTRIBUTES_VISIBILITY.index(visibleAttrName) 
            headerView.swapSections(currentVisibilityIndex, targetVisibilityIndex)
             
            self.resizeColumnToContents(visibleColumns[visibleAttrName])
                 
        self.sortByColumn(visibleColumns[self.DFT_ATTRIBUTES_VISIBILITY[0]], QtCore.Qt.AscendingOrder)
        
#         self.header().setStretchLastSection(False)
#         self.header().setResizeMode(0, QtGui.QHeaderView.Stretch)
        #self.header().setResizeMode(self.header().count()-1, QtGui.QHeaderView.Fixed)
        
#         self.header().setResizeMode(self.header().count()-1, QtGui.QHeaderView.ResizeToContents)
#         self.header().resizeSection(self.header().count()-1, 20)
#         self.header().setResizeMode(self.header().count()-1, QtGui.QHeaderView.Stretch)        
        
    #--------------------------------------------------------------------------

    def showHeaderColumnOptions(self, value):
                
        if value == self.header().count()-1:
            #headerButtonItem = self.model().horizontalHeaderItem(value)            
            
            currentQMenu = QtGui.QMenu()
            for column, label in enumerate(self.model().headerLabels[:-1]):
                currentQAction = QtGui.QAction('%s' % label, currentQMenu)
                currentQAction.setCheckable(True)
                currentQAction.setChecked(self.headerColumnVisibility[column])
                currentQAction.toggled.connect(partial(self.setColumnVisible, column))
                
                currentQMenu.addAction(currentQAction)
            
            currentQMenu.exec_(QtGui.QCursor.pos())
                
    #--------------------------------------------------------------------------

    def setColumnVisible(self, column, isChecked):
        if isChecked:
            self.showColumn(column)
            self.resizeColumnToContents(column)
            
            # set default sorting to current column
            self.header().setSortIndicator(column, QtCore.Qt.AscendingOrder)
        else:
            self.hideColumn(column)
            # set default sorting to current column
            self.header().setSortIndicator(21, QtCore.Qt.AscendingOrder)
        
        self.headerColumnVisibility[column] = isChecked
        
        self.headerColumnVisibilityChanged.emit([])
    
    #--------------------------------------------------------------------------
    
    def toTree(self):
        
        headerColumnVisibility = dict()
        
        for column, label in enumerate(self.model().headerLabels[:-1]):
            if self.headerColumnVisibility[column]:
                headerColumnVisibility[label] = str(self.headerColumnVisibility[column])
        
        element = ETree.Element(self.TAG)
        ETree.SubElement(element, 'columnVisibility', headerColumnVisibility)
        
        return element
    
    #--------------------------------------------------------------------------
    
    def fromTree(self, element):
        
#         print ETree.tostring(element)
        columnVisibilityElement = element.find('columnVisibility')
        for name, value in columnVisibilityElement.items():
            column = self.model().headerLabels.index(name)
            self.setColumnVisible(column, True)
                 
#===============================================================================

def createDock(parent, label, widget):

    dockWidget = QtGui.QDockWidget(label, parent)
    dockWidget.setWidget(widget)
        
    return dockWidget
            

#=============================================================================

