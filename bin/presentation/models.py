#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys

from functools import partial
import numpy as np

from PyQt4 import QtCore
from PyQt4 import QtGui

from domain import utils
from domain import enum_items as ei
from domain import base_items as bi
from domain import comp_items as ci

#=============================================================================

class BaseAttributeTreeItem(QtGui.QStandardItem):
    
    ICON_PATH = ''
    
    def __init__(self, name, dataItem=None, attributeName=''):
        
        self.dataItem = dataItem
        
        super(BaseAttributeTreeItem, self).__init__(name)
        
        self.setIcon(QtGui.QIcon(self.ICON_PATH))
        self.setToolTip(attributeName)
        self.setEditable(False)
        
        self.setForeground(self.dataItem.solverType.JOB_ITEM_COLOUR)
        if self.dataItem.isOutOfTheQueue:
            self.setForeground(utils.TreeItemColors.RED)
            
    #------------------------------------------------------------------------------ 
    
    def openContextMenu(self, parentWidget):
        
        menu = QtGui.QMenu()
        
        jobInfoAction = menu.addAction('Job info')
        jobContentAction = menu.addAction('Check progress')
        jobKillAction = menu.addAction('Terminate')
        
        jobInfoAction.triggered.connect(self._jobInfo)
        jobContentAction.triggered.connect(
            lambda: self._showContent(parentWidget))
        jobKillAction.triggered.connect(self._jobTerminate)
        
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
    
    def _jobTerminate(self):
        
        quitMsg = "Are you sure to terminate the job?"
        reply = QtGui.QMessageBox.question(None, 'Exit', 
            quitMsg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
    
        if reply == QtGui.QMessageBox.Yes:
            status = self.dataItem.terminate()
        
            QtGui.QMessageBox.information(None, 'Terminate job %s info' % self.dataItem.id,
                    str(status))
    
    #------------------------------------------------------------------------------ 
    
    def _jobInfo(self):
        
        QtGui.QMessageBox.information(None, 'Job %s info' % self.dataItem.id,
                str(self.dataItem.getInfo()))
        
    #------------------------------------------------------------------------------ 
    
    def _showContent(self, parentWidget):
        
        parentWidget.itemForTrackingSelected.emit(self.dataItem)
            
            
#=============================================================================

class QueueJobTreeItem(QtCore.QObject):
    
    ICON_PATH = ''
    hasFinished = QtCore.pyqtSignal(object)
    
    def __init__(self, dataItem):
        
        self.dataItem = dataItem
        
        super(QueueJobTreeItem, self).__init__()
#         super(QueueJobTreeItem, self).__init__(self.dataItem.name)
#         
#         self.setIcon(QtGui.QIcon(self.ICON_PATH))
#         self.setToolTip(self.dataItem.name)
#         self.setEditable(False)
        
        self.attributeItems = dict()
    
    #------------------------------------------------------------------------------ 
    
    def updateAttributes(self):
        
        for attrituteName in self.dataItem.getListOfAttributes():
            # this should never happen
            if attrituteName not in self.attributeItems:
                continue
            
            attrModelItem = self.attributeItems[attrituteName]
            data = self.dataItem.getAttribute(attrituteName)
            if data != attrModelItem.data(QtCore.Qt.DisplayRole):
                attrModelItem.setData(data, QtCore.Qt.DisplayRole)
                    
    #------------------------------------------------------------------------------ 
    
    def getRow(self):
        
        row = []
        
        for attrituteName in self.dataItem.getListOfAttributes():
            data = self.dataItem.getAttribute(attrituteName)
            
            attrModelItem = BaseAttributeTreeItem(data, self.dataItem, attrituteName)
            row.append(attrModelItem)
            self.attributeItems[attrituteName] = attrModelItem
        
        return row
    
    #------------------------------------------------------------------------------
    
    def parentJobFinished(self):
        
        attrModelItem = self.attributeItems[self.attributeItems.keys()[0]]
        self.hasFinished.emit(attrModelItem)
    
    #------------------------------------------------------------------------------ 
#     
#     def openContextMenu(self, parentView):
#         
#         menu = QtGui.QMenu()
#         collapseAction = menu.addAction("Collapse children")
#         collapseAction.triggered.connect(lambda: self._collapseChildren(parentView))
#         
#         menu.exec_(QtGui.QCursor.pos())
#     
#     #------------------------------------------------------------------------------ 
#     
#     def _collapseChildren(self, parentView):
#             
#         for row in range(self.rowCount()):
#             child = self.child(row)
#             parentView.collapse(child.index())
    
    
#=============================================================================

class BaseListWidgetItem(QtGui.QListWidgetItem):
    
    ICON_PATH = os.path.join(utils.PATH_ICONS, 'mail-tagged.png')
    
    def __init__(self, dataItem):
        
        self.dataItem = dataItem
        
        super(BaseListWidgetItem, self).__init__(self.dataItem.name)
        
        self.setIcon(QtGui.QIcon(self.ICON_PATH))
        self.setToolTip(self.dataItem.name)
        #self.setEditable(True)
        self.setFlags(self.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable)
        self.setCheckState(QtCore.Qt.Unchecked)
#         setFlags (item->flags () & Qt::ItemIsEditable)
    
    #------------------------------------------------------------------------------ 
    
    def openContextMenu(self, parentWidget):
        
        pass

#=============================================================================
# 
# class MaterialImporterListWidgetItem(BaseListWidgetItem):
#         
#     #------------------------------------------------------------------------------ 
#     
#     def openContextMenu(self, parentWidget):
#         
#         menu = QtGui.QMenu()
#         separateMenu = menu.addMenu("Separate material definition")
#         
#         for stateVariable in ei.MATERIAL_SPLITTER_STATE_VARIABLES:
#             tempSepAction = separateMenu.addAction(stateVariable)
#             tempSepAction.triggered.connect(
#                 #lambda: self.separateMaterial(parentWidget, stateVariable))
#                 partial(self.separateMaterial, parentWidget, stateVariable))
#             
#         menu.exec_(QtGui.QCursor.pos())
#     
#     #------------------------------------------------------------------------------ 
#     
#     def separateMaterial(self, parentWidget, stateVariable):
#                 
#         parentDialog = parentWidget.parentWidget
#         parentDialog.splitMaterial(self.dataItem, stateVariable)
        



#=============================================================================

# class SelectedMaterialItem(QtGui.QStandardItem):
#     
#     ICON_PATH = MaterialTreeItem.ICON_PATH
#     DFT_COLOUR = QtGui.QBrush(QtCore.Qt.black)
#     
#     def __init__(self, dataItem):
#         
#         self.dataItem = dataItem
#         
#         super(SelectedMaterialItem, self).__init__(self.dataItem.name)
#         
#         self.setIcon(QtGui.QIcon(self.ICON_PATH))
#         self.setToolTip(self.dataItem.name)
#         #self.setEditable(True)
#         self.setFlags(self.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable)#^ QtCore.Qt.QtItemIsDropEnabled)
#         self.setFlags(self.flags() & ~QtCore.Qt.ItemIsDropEnabled)
#         self.setCheckState(QtCore.Qt.Unchecked)
#         
#         # this avoids the Qt object pickle error but requires further improvements
# #         self.setData(self.dataItem.parentItem(), QtCore.Qt.UserRole)
#         self.setData(self.dataItem, QtCore.Qt.UserRole)
#         self.dataItem.setTreeItem(self)
#         
#     #------------------------------------------------------------------------------ 
#     
#     def getRow(self):
#         
#         row = [self]
#         
#         if len(self.dataItem.getListOfAttributes()) == 0:
#             return
# 
#         for attrituteName in ei.allAttributes():
#             if attrituteName in self.dataItem.getListOfAttributes():
#                 data = self.dataItem.getAttribute(attrituteName)
#             else:
#                 data = ''     
#                      
#             if data is None:
#                 data = ''
#             
#             attrModelItem = QtGui.QStandardItem(data)
#             attrModelItem.setToolTip(data)
#             attrModelItem.setEditable(False)
#             row.append(attrModelItem)
#         
#         return row
#     
#     #------------------------------------------------------------------------------ 
#     
#     def setColour(self, rgb):
#         
#         self.setForeground(QtGui.QBrush(QtGui.QColor.fromRgbF(*rgb)))
#     
#     #------------------------------------------------------------------------------ 
#     
#     def setDftColour(self):
#         
#         self.setForeground(self.DFT_COLOUR)
#         
#     #------------------------------------------------------------------------------ 
#     
#     def openContextMenu(self, parentWidget):
#         
#         menu = QtGui.QMenu()
#         calculationsMenu = menu.addMenu("Calculations")
#         action = calculationsMenu.addAction('Norm data')
#         action.setCheckable(True)
#         action.setChecked(self.dataItem.isNormBase)
#         action.toggled.connect(
#             lambda: self.setAsNormBase(parentWidget))
#                 
#         addAction = calculationsMenu.addAction('Add')
#         
#         subsMenu = calculationsMenu.addMenu('Subtract')
#         fFsSubAction = subsMenu.addAction('1st - 2nd')
#         sFfSubAction = subsMenu.addAction('2nd - 1st')
#         
#         multiplyAction = calculationsMenu.addAction('Multiply')
#         
#         divideMenu = calculationsMenu.addMenu('Divide')
#         fFsDivAction = divideMenu.addAction('1st / 2nd')
#         sFfDivAction = divideMenu.addAction('2nd / 1st')
#         
#         if len(parentWidget.currentCheckedItems) > 1:
#             addAction.setEnabled(True)
#             subsMenu.setEnabled(True)
#             multiplyAction.setEnabled(True)
#             divideMenu.setEnabled(True)
#         else:
#             addAction.setEnabled(False)
#             subsMenu.setEnabled(False)
#             multiplyAction.setEnabled(False)
#             divideMenu.setEnabled(False)
#         
#         toolsMenu = menu.addMenu("Tools")
#         separateMenu = toolsMenu.addMenu("Separate material definition")
#         
#         # data conversion
#         convertionMenu = toolsMenu.addMenu('Convert')
#         convertionMenu.addAction('Eng.stress -> True stress')
#         
#         for stateVariable in ei.MATERIAL_SPLITTER_STATE_VARIABLES:
#             tempSepAction = separateMenu.addAction(stateVariable)
#             tempSepAction.triggered.connect(
#                 #lambda: self.separateMaterial(parentWidget, stateVariable))
#                 partial(self.separateMaterial, parentWidget, stateVariable))
#         
#         exportMenu = menu.addMenu("Export data")
#         exportToTableAction = exportMenu.addAction('To *.csv')
#         exportToTableAction.triggered.connect(
#             lambda: self.exportCurveData(parentWidget))
#         
#         if self.checkState() > 1:
#             exportMenu.setEnabled(True)
#         else:
#             exportMenu.setEnabled(False)
#         
#         menu.addSeparator()
#         deleteAction = menu.addAction('Delete')
#         deleteAction.triggered.connect(
#             lambda: self._removeItem(parentWidget))
#         
#         menu.exec_(QtGui.QCursor.pos())
#     
#     #------------------------------------------------------------------------------ 
#     
#     def _removeItem(self, parentWidget):
#         
#         parentWidget.model().takeRow(
#             parentWidget.model().indexFromItem(self).row())
#         parentWidget.itemRemoved.emit()
#     
#     #------------------------------------------------------------------------------ 
#     
#     def setAsNormBase(self, parentWidget):
#         
#         state = not self.dataItem.isNormBase
#         # reset all items in the list
#         parentWidget.cancelNorm(update = False)
#         
#         self.dataItem.isNormBase = state
#         
#         parentWidget.parentApplication.signalController.updateGraph.emit([])
#     
#     #------------------------------------------------------------------------------ 
#     
#     def exportCurveData(self, parentWidget):
#         
#         parentWidget.parentApplication.signalController.exportCurveDataToTable.emit(
#             [self.dataItem])
# 
#     #------------------------------------------------------------------------------ 
#     
#     def separateMaterial(self, parentWidget, stateVariable):
#                 
#         parentWidget.splitMaterial(self.dataItem, stateVariable)
#                 



#=================================================================================

class BaseTreeModel(QtGui.QStandardItemModel):
    
    def __init__(self):
        
        super(BaseTreeModel, self).__init__()
        
        self.headerLabels = []
        
#         self.setHorizontalHeaderItem(0, QtGui.QStandardItem('Material database'))
#         button = QtGui.QStandardItem('Add attribute')
#         self.setHorizontalHeaderItem(1, button)
        
#         for attrituteName in ei.MATERIAL_ATTRIBUTES_TXT:
        for attrituteName in sorted(ci.RunningJob.ATTRIBUTE_NAMES):
            self.headerLabels.append(attrituteName)
        
        #self.headerLabels.append('v')
        #self.headerLabels.append(QtCore.QString.fromUtf8('&#9660'))
        self.headerLabels.append(u'\u25BC')
        self.setHorizontalHeaderLabels(self.headerLabels)
    
    #------------------------------------------------------------------------------ 
#     
#     def getAttributeColumnIndex(self, attributeName):
#         
#         if attributeName not in self.headerLabels:
#             self.headerLabels.append(attributeName)
#             
#         return self.headerLabels.index(attributeName)
    
    


#=================================================================================























