#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Python script for '''

import os
import sys

import pickle

import xml.etree.ElementTree as ETree

from domain import utils
# from presentation import models

#==============================================================================

class GridEngineInterfaceException(Exception): pass

#=============================================================================

class GridEngineInterface(object):
    
        
    #--------------------------------------------------------------------------
    @staticmethod
    def getHostsStat():
        
        stdout, _ = utils.runSubprocess('qhost -j -xml')
                
        rootElement = ETree.fromstring(stdout)  
        
        hosts = dict()
        for hostElement in rootElement.iter('host'):
            hostName = hostElement.attrib['name']
            hosts[hostName] = dict()
            for hostValueElement in hostElement.iter('hostvalue'):
                hostAttributeName = hostValueElement.attrib['name']
                hosts[hostName][hostAttributeName] = hostValueElement.text
            
            # add running jobs
            hosts[hostName]['jobs'] = dict()
            for jobElement in hostElement.iter('job'):
                jobId = jobElement.attrib['name']
                hosts[hostName]['jobs'][jobId] = dict()
                for jobValueElement in jobElement:
                    jobAttributeName = jobValueElement.attrib['name']
                    hosts[hostName]['jobs'][jobId][jobAttributeName] = jobValueElement.text
            
        return hosts
        
#=============================================================================

# class UserSettings(object):
#     
#     SETTINGS_DIR = '.materialDB'
#     TAG = 'MaterialDB_user_settings'
#     
#     def __init__(self, parentApplication):
#         
#         self.parentApplication = parentApplication
#         
#         userDir = os.path.join(os.path.expanduser('~'), self.SETTINGS_DIR)
#         if not os.path.exists(userDir):
#             os.makedirs(userDir)
#     
#     #--------------------------------------------------------------------------
#     
#     def _getUserSettingsPath(self):
#     
#         userSettingPath = os.path.join(os.path.expanduser('~'), self.SETTINGS_DIR,
#             utils.USER_CONFIG_SETTINGS_FILE)
#         
#         return userSettingPath
#     
#     #--------------------------------------------------------------------------
#     
#     def save(self):
#         
#         mainWindow = self.parentApplication.mainWindow
#         
#         rootElement = ETree.Element(self.TAG)
#         
#         # DB navigation widget settings
#         databaseTreeView = mainWindow.navigationWidget.databaseTreeView
#         databaseTreeViewElement = databaseTreeView.toTree()
#         rootElement.append(databaseTreeViewElement)
#         
#         # get DB tree structure
#         DBtreeStructureElement = ETree.Element('treeStructure',
#             {'structure' : pickle.dumps(models.TreeCreator.DB_TREE_DEFINITION)})
#         databaseTreeViewElement.append(DBtreeStructureElement)
#         
#         # write file
#         fo = open(self._getUserSettingsPath(), 'wt')
#         fo.write(ETree.tostring(rootElement))
#         fo.close()
#     
#     #--------------------------------------------------------------------------
#     
#     def load(self):
#         
#         userSettingFilePath = self._getUserSettingsPath()
#         
#         if not os.path.isfile(self._getUserSettingsPath()):
#             return False
#         
#         mainWindow = self.parentApplication.mainWindow
#         
#         tree = ETree.parse(userSettingFilePath)  
#         rootElement = tree.getroot()
#         
# #         print ETree.tostring(rootElement)
#         
#         databaseTreeView = mainWindow.navigationWidget.databaseTreeView
#         databaseTreeViewElement = rootElement.find(databaseTreeView.TAG)
#         databaseTreeView.fromTree(databaseTreeViewElement)
#         
#         # set DB tree structure
#         DBtreeStructureElement = databaseTreeViewElement.find('treeStructure')
#         treeStructure = pickle.loads(DBtreeStructureElement.get('structure'))
#                          
#         if type(treeStructure) is list and len(treeStructure) > 0:
#             models.TreeCreator.setTreeStructure(treeStructure)
#         
#         return True
        
        
        
        
        
        
        