#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import glob

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
        self.items = list()
        
        self._setupWidgets()
        self._setupConnections()
    
    #---------------------------------------------------------------------------
    
    def _setupWidgets(self):
        
        self.setLayout(QtGui.QVBoxLayout())
        
        groupLayout = QtGui.QVBoxLayout()
        group = QtGui.QGroupBox('Select input file(s)')
        group.setLayout(groupLayout)
        
        self.workingDirectorySelectorWidget = WorkingDirectorySelectorWidget(self.selectorItem)
        self.listWidget = QtGui.QListWidget()
        
        groupLayout.addWidget(self.workingDirectorySelectorWidget)
        groupLayout.addWidget(self.listWidget)
        self.layout().addWidget(group)
                
        # buttons
        self.checkAllButton = QtGui.QPushButton('Check all')
        self.checkNoneButton = QtGui.QPushButton('Check none')
        
        buttonLayout = QtGui.QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.checkAllButton)
        buttonLayout.addWidget(self.checkNoneButton)
        buttonLayout.addStretch()
        
        self.layout().addLayout(buttonLayout)

    #---------------------------------------------------------------------------
    
    def _setupConnections(self):
        
        self.checkAllButton.released.connect(self._checkAll)
        self.checkNoneButton.released.connect(self._checkNone)
        self.listWidget.itemClicked.connect(self.valueChanged)
        
        self.workingDirectorySelectorWidget.changed.connect(self.findInputFiles)
    
    #---------------------------------------------------------------------------
    
    def _checkAll(self):
        
        for item in self.items:
            item.setCheckState(2)
        
        self.valueChanged()
    
    #---------------------------------------------------------------------------
    
    def _checkNone(self):
        
        for item in self.items:
            item.setCheckState(0)
        
        self.valueChanged()
        
    #---------------------------------------------------------------------------

    def setupInputFiles(self):
                
        self.listWidget.clear()
        self.items = list()
        
        for option in self.selectorItem.getOptions():
            
            item = QtGui.QListWidgetItem(os.path.basename(option))
            item.setCheckState(0)
            self.listWidget.addItem(item)
                        
            self.items.append(item)
        
        if len(self.items) == 1:
            defaultItem = self.items[0]
            defaultItem.setCheckState(2)
            
            self.valueChanged()
    
    #---------------------------------------------------------------------------
    
    def getSelection(self):
        
        options = self.selectorItem.getOptions()
        
        checkedOptions = list()
        for index, item in enumerate(self.items):
            if item.checkState() == QtCore.Qt.Checked:
                checkedOptions.append(options[index])
        
        return checkedOptions
    
    #---------------------------------------------------------------------------
    
    def valueChanged(self):
        
        self.changed.emit(self.getSelection())
    
    #--------------------------------------------------------------------------

    def findInputFiles(self, projectDir):

        self.selectorItem.parentApplication.setWorkDir(projectDir)
        
        self.workingDirectorySelectorWidget.lineEdit.setText(projectDir)
        
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
    
    #--------------------------------------------------------------------------

    def itemRenamed(self, editedItem):
        
        editedItem.dataItem.setAttribute('NAME', unicode(editedItem.text()))
        
        self.itemNameChanged.emit([editedItem.dataItem])
    
    #--------------------------------------------------------------------------

    def itemSelected(self):
        
        pass
    
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

class QueueJobListWidgetItem(BaseListWidgetItem):
    
    def __init__(self, dataItem):
        super(QueueJobListWidgetItem, self).__init__(dataItem)
        
        
        if 'abaqus' in self.dataItem.licenceServer.CODE:
            self.setTextColor(QtGui.QColor("blue"))
        elif 'pamcrash' in self.dataItem.licenceServer.CODE:
            self.setTextColor(QtGui.QColor("green"))
        
        if self.dataItem.isOutOfTheQueue:
            self.setTextColor(QtGui.QColor("red"))
            
    #------------------------------------------------------------------------------ 
    
    def openContextMenu(self, parentWidget):
        
        menu = QtGui.QMenu()
        
        jobInfoAction = menu.addAction('Job info')
        jobContentAction = menu.addAction('Check progress')
        jobKillAction = menu.addAction('Terminate')
        
        jobInfoAction.triggered.connect(self.jobInfo)
        jobContentAction.triggered.connect(
            lambda: self.showContent(parentWidget))
        jobKillAction.triggered.connect(self.jobTerminate)
        
        # check autority
#         if parentWidget.parentApplication.userName != self.dataItem['JB_owner']:
#             jobKillAction.setEnabled(False)
        if self.dataItem.isOutOfTheQueue:
            jobKillAction.setEnabled(False)
        
        if self.dataItem.isOutOfTheQueue:
            jobContentAction.setEnabled(False)
        elif self.dataItem._attributes['state'] != 'r':
            jobContentAction.setEnabled(False)
                    
        menu.exec_(QtGui.QCursor.pos())
    
    #------------------------------------------------------------------------------ 
    
    def jobTerminate(self):
        
        quitMsg = "Are you sure to terminate the job?"
        reply = QtGui.QMessageBox.question(None, 'Exit', 
            quitMsg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
    
        if reply == QtGui.QMessageBox.Yes:
            status = self.dataItem.terminate()
        
            QtGui.QMessageBox.information(None, 'Terminate job %s info' % self.dataItem.id,
                    str(status))
    
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
        self.addTab(TrackedFileContentWidget(self, jobItem, fileName), name)
        
        

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
            self.fileContentTrackerThread.run)
        
        # initiate content
        self._updateContent(self.dataItem.getTrackedFileContent(self.fileName))
        
    #------------------------------------------------------------------------------ 
    
    def _updateContent(self, trackedFileContent):
        
        self.fileContentTextEdit.clear()
        
        self.fileContentTextEdit.setText(trackedFileContent)
        

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

def createDock(parent, label, widget):

    dockWidget = QtGui.QDockWidget(label, parent)
    dockWidget.setWidget(widget)
        
    return dockWidget
            

#=============================================================================

