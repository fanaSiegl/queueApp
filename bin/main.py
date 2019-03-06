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

APPLICATION_NAME = 'project_name'
DOCUMENTATON_GROUP = 'tool documentation group'
DOCUMENTATON_DESCRIPTION = 'Python application one line description.'

#==============================================================================

import os
import sys
import traceback

from domain import utils
from domain import base_items as bi
from domain import comp_items as ci

from persistent import file_items as fi

#==============================================================================

DEBUG = 1

#==============================================================================

class QabaException(Exception): pass

#==============================================================================
    
class Qaba(object):
    
    APPLICATION_NAME = 'qaba'
    
    def __init__(self, args):
        
        self.workDir = os.getcwd()
                
        self.jobs = list()
        
        # initiate resource status
        bi.BaseExecutionServerType.connectResources()
                
        
        self.profile = self.setProfile()
        self.profile.runDataSelectionSequence()       
                
        for inpFileName in self.profile.inpFileNames:
            newJob = self.profile.job.getCopy()
            newJob.setInpFile(inpFileName)
            newJob.setExecutableFile(fi.AbaqusJobExecutableFile(self, newJob))
        
            self.jobs.append(object)
        
#             print newJob.executableFile.getContent()
            
            newJob.executableFile.save()
                    
        print 'Finished'

    #--------------------------------------------------------------------------
    
    def setProfile(self):
        
        profileSelector = ci.ExecutionProfileSelector(self)
        profileType = profileSelector.getSelection()
        
        return profileType(self)
            
    

#==============================================================================

def main():
        
    
    try:
        qaba = Qaba(sys.argv)
    except Exception as e:
        print str(e)
        if DEBUG:
            traceback.print_exc()
    
       
#==============================================================================

if __name__ == '__main__':
    main()
    