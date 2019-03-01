#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Python script for '''

import os
import sys
import ConfigParser
import numpy as np
import subprocess

#==============================================================================

PATH_BIN = os.path.normpath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)),'..'))
PATH_INI = os.path.normpath(os.path.join(PATH_BIN,'..', 'ini'))
PATH_DOC = os.path.normpath(os.path.join(PATH_BIN,'..', 'doc'))
PATH_RES = os.path.normpath(os.path.join(PATH_BIN,'..', 'res'))
PATH_ICONS = os.path.join(PATH_RES, 'icons')

VERSION_FILE = 'version.ini'

#==============================================================================

def getVersionInfo():

    SECTION_VERSION = 'VERSION'
     
    config = ConfigParser.ConfigParser()
     
    cfgFileName = os.path.join(PATH_INI, VERSION_FILE)
    config.read(cfgFileName)
         
    revision = config.get(SECTION_VERSION, 'REVISION')
    modifiedBy = config.get(SECTION_VERSION, 'AUTHOR')
    lastModified = config.get(SECTION_VERSION, 'MODIFIED')
 
    return revision, modifiedBy, lastModified

#==============================================================================

def runSubprocess(command, cwd=None):
    
    process = subprocess.Popen(
        command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        cwd=cwd)
    
    return process.communicate()

#==============================================================================
    