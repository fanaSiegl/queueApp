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

from domain import utils
from domain import base_items as bi
from domain import comp_items as ci
from domain import enum_items as ei

#==============================================================================

DEBUG = 1

#==============================================================================

class QabaException(Exception): pass

#==============================================================================
    
class Qaba(object):
        
    def __init__(self, args):
        
        self.workDir = os.getcwd()
        
        checkProjectPath(self.workDir)
        
        self.jobs = list()
        
        # initiate resource status
        bi.BaseExecutionServerType.connectResources()
                
        self.profile = self.setProfile()
        self.profile.runDataSelectionSequence()       
                
        for inpFileName in self.profile.inpFileNames:
            newJob = self.profile.job.getCopy()
            newJob.setInpFile(inpFileName)
            newJob.setExecutableFile(newJob.EXECUTABLE_FILE_TYPE(self, newJob))
            newJob.executableFile.save()
            self.jobs.append(object)
            
            utils.runSubprocess('qsub %s' % newJob.executableFile.outputFileName)

    #--------------------------------------------------------------------------
    
    def setProfile(self):
        
        profileSelector = ci.AbaqusExecutionProfileSelector(self)
        profileType = profileSelector.getSelection()
        
        return profileType(self)

#==============================================================================
    
class Qpam(Qaba):
             
    def setProfile(self):
                
        profileSelector = ci.PamCrashExecutionProfileSelector(self)
        profileType = profileSelector.getSelection()
        
        return profileType(self)

#==============================================================================

class Queue(object):
    
    def __init__(self):
        
        bi.BaseExecutionServerType.connectResources()
        self.q = bi.Queue()
        
        while True:
            bi.BaseExecutionServerType.connectResources()
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
    bi.BaseExecutionServerType.connectResources()
    
    hosts = list()
    for licenseServer in bi.LICENSE_SERVER_TYPES:
        hosts.extend(
            [currentHost.name for currentHost in licenseServer.getAvailableHosts()])
    
    return sorted(set(hosts))

#==============================================================================

def main():
         
#     parser = argparse.ArgumentParser(description=__doc__[:__doc__.find('Usage')],
#         formatter_class=argparse.RawDescriptionHelpFormatter)
#     parser.add_argument('-g', action='store_true', help='Run gui.')
#     parser.add_argument('-inp', nargs=1, metavar='inp_path', dest='inpFilePath',
#         help='ABAQUS Input file path.')
#     parser.add_argument('-license',
#         choices=[licenseServer.NAME for licenseServer in bi.LICENSE_SERVER_TYPES],
#         help='ABAQUS license server type.')
#     parser.add_argument('-solver', choices=ei.ABAQUS_SOLVER_LIST,
#         help='ABAQUS solver version.')
#     parser.add_argument('-host', choices=getListOfHosts(),
#         help='Calculation host.')
#     parser.add_argument('-cpu', nargs=1, help='Number of CPUs.')
#     parser.add_argument('-gpu', nargs=1, help='Number of GPUs.')
#     parser.add_argument('-prio', nargs=1, help='Job priority.')
#     parser.add_argument('-start', nargs=1, help='Job start time.')
#     parser.add_argument('-des', nargs=1, help='Job description (max. 15 characters).')
#     parser.add_argument('-param', nargs=1, help='Additional ABAQUS parameters: "-x y -xx yy" (max 15 characters).')
#      
#     args = parser.parse_args()
        
    try:
#         qpam = Qpam(args)
#         qaba = Qaba([])
        q = Queue()
    except Exception as e:
        print str(e)
        if DEBUG:
            traceback.print_exc()
     
        
#==============================================================================
 
# if __name__ == '__main__':
#     main()
    