#!/usr/bin/python
# -*- coding: utf-8 -*-

''' Python script for ...'''

import os
import sys
import re
import shutil
from functools import partial

from PyQt4 import QtCore
from PyQt4 import QtGui
# from PyQt4 import QtWebKit

from presentation import base_widgets as bw

from domain import utils
from domain import base_items as bi

#==============================================================================

class LinceseRestrictionSettingDialog(QtGui.QDialog):

    WIDTH = 1000
    HEIGHT = 200
    
    TITLE = 'License restriction settings'
    
    def __init__(self, parentApplication):
        super(LinceseRestrictionSettingDialog, self).__init__()
        
        self.parentApplication = parentApplication
        
        self.restrictionInitialSettings = utils.getRestrictionConfig()
        self.restrictionSettings = dict()
        
        self._setWindowGeometry()
        self._setupWidgets()
        self._setupConnections()
        
        self._setupContent()
        
    #---------------------------------------------------------------------------

    def _setWindowGeometry(self):
        
        self.setWindowTitle(self.TITLE)

        self.resize(self.WIDTH, self.HEIGHT)
        self.move(QtGui.QApplication.desktop().screen().rect().center()- self.rect().center())
    
    #---------------------------------------------------------------------------

    def _setupConnections(self):
                
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
    #---------------------------------------------------------------------------

    def _setupWidgets(self):
        
        self.setLayout(QtGui.QVBoxLayout())
        
        settingsLaytout = QtGui.QGridLayout()
                
        for rowNo, licenceServer in enumerate(bi.LICENSE_SERVER_TYPES):
                        
            comboBox = QtGui.QComboBox()
            settingStackWidget = QtGui.QStackedWidget()
            
            self.restrictionSettings[licenceServer] = settingStackWidget
            
            settingsLaytout.addWidget(QtGui.QLabel(licenceServer.NAME), rowNo, 0)
            settingsLaytout.addWidget(comboBox, rowNo, 1)
            settingsLaytout.addWidget(settingStackWidget, rowNo, 2)
            
            # initiate content from existing settings
            initialSettings = self.restrictionInitialSettings[licenceServer.NAME]
            
            activeRestriction = bi.BaseLicenseRestrictionType.getFromConfig(
                licenceServer.NAME, initialSettings)
            
            for restrictionName in bi.LICENSE_RESTRICTION_TYPES.keys():
                comboBox.addItem(restrictionName)
                
                restrictionSettingWidget = bw.LICENSE_RESTRICTION_TYPE_WIDGETS[restrictionName]()
                
                if activeRestriction.NAME == restrictionName:
                    restrictionSettingWidget.setConfig(activeRestriction)
                
                settingStackWidget.addWidget(restrictionSettingWidget)
            
            comboBox.currentIndexChanged.connect(
                partial(self.restrictionChanged, licenceServer.NAME, comboBox, settingStackWidget))
            
            comboBox.setCurrentIndex(comboBox.findText(activeRestriction.NAME))
            
        self.layout().addLayout(settingsLaytout)
            
        # buttons
        frame = QtGui.QFrame()
        frame.setFrameShape(QtGui.QFrame.HLine)
        self.layout().addWidget(frame)
         
        self.buttonBox = QtGui.QDialogButtonBox()
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Cancel)

        self.layout().addWidget(self.buttonBox)
    
    #---------------------------------------------------------------------------
    
    def restrictionChanged(self, licenseServerTypeName, comboBox, settingStackWidget):
        
        settingStackWidget.setCurrentIndex(comboBox.currentIndex())
        
    #---------------------------------------------------------------------------

    def _setupContent(self):
        
        pass
    
    #---------------------------------------------------------------------------
    
    def accept(self):
        
        settings = dict()
        for licenceServer, settingStackWidget in self.restrictionSettings.iteritems():
            currentSettingWidget = settingStackWidget.currentWidget()
            restriction = bi.BaseLicenseRestrictionType.getFromConfig(
                licenceServer.NAME, currentSettingWidget.getConfig())
                        
            licenceServer.setRestriction(restriction)
            
            settings[licenceServer.NAME] = currentSettingWidget.getConfig()
        
        utils.setRestrictionConfig(settings)
                
        super(LinceseRestrictionSettingDialog, self).accept()    

#==============================================================================

