#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Python script for '''

import os
import sys

import pickle

import xml.etree.ElementTree as ETree
import xml.dom.minidom

from domain import utils
# from presentation import models

#==============================================================================

class GridEngineInterfaceException(Exception): pass

#=============================================================================

class GridEngineInterface(object):
    
        
    #--------------------------------------------------------------------------
    @staticmethod
    def getHostsStat():
        
        ''' Returns a list of all hosts - execution servers and their running
        jobs.
        
        '''
        
        stdout, _ = utils.runSubprocess('qhost -j -xml')
                
        rootElement = ETree.fromstring(stdout)  
        
        hosts = dict()
        for hostElement in rootElement.iter('host'):
            hostName = hostElement.attrib['name']
            
            # skip global host
            if hostName == 'global' or 'test' in hostName:
                continue
            
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
    
    #--------------------------------------------------------------------------
    @staticmethod
    def getQueueStat():
        
        stdout, _ = utils.runSubprocess('qstat -u \* -xml -r')        
        
        rootElement = ETree.fromstring(stdout)
        
        jobElements = list()
        for elem in rootElement.iter():
            if elem.tag == 'job_list':
                jobElements.append(elem)
        
        jobs = list()
        for jobElement in jobElements:
#             jobState = jobElement.get('state')
#             if jobState not in jobs:
#                 jobs[jobState] = list()            
            elemAttributes = dict()
            for attributeElement in jobElement.getchildren():
                elemAttributes[attributeElement.tag] = attributeElement.text 
#             jobs[jobState].append(elemAttributes)
            jobs.append(elemAttributes)
        
        return jobs
    
    #--------------------------------------------------------------------------
    @staticmethod
    def getAvailableHost(licenseServerName):
        
        stdout, _ = utils.runSubprocess('qstat -f -q %s -xml' % licenseServerName)
            
        rootElement = ETree.fromstring(stdout)
        
        hosts = list()
        for hostElement in rootElement.iter('Queue-List'):
            hostName = hostElement.find('name').text
            hosts.append(hostName.split('@')[-1])
        
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
        
        
        
#==============================================================================

        
        
        