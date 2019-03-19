#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Python script for '''

import os
import sys
import ConfigParser
import subprocess
import getpass
import socket
import logging

#==============================================================================

PATH_BIN = os.path.normpath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)),'..'))
PATH_INI = os.path.normpath(os.path.join(PATH_BIN,'..', 'ini'))
PATH_DOC = os.path.normpath(os.path.join(PATH_BIN,'..', 'doc'))
PATH_RES = os.path.normpath(os.path.join(PATH_BIN,'..', 'res'))
PATH_ICONS = os.path.join(PATH_RES, 'icons')

VERSION_FILE = 'version.ini'
LOG_FILE = 'queueApp.log'

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

def runSubprocess(command, returnOutput=True, cwd=None):
    
    process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, cwd=cwd)
    
    if returnOutput:
        return process.communicate()
    
#===============================================================================

def registerClass(cls):
    
    if type(cls.container) is dict:
        cls.container[cls.NAME] = cls
    elif type(cls.container) is list:
        
        if hasattr(cls, 'ID'):
            if cls.ID >= len(cls.container):
                cls.container.extend((cls.ID - len(cls.container) + 1)*[None])
            cls.container[cls.ID] = cls
        else:
            cls.container.append(cls)
            
    return cls

#==============================================================================

def getUserInfo():
    
    userName = getpass.getuser()
    machine = socket.gethostname()
    
    if 'GE_MAIL' in os.environ:
        email = os.environ['GE_MAIL']
    else:
        email = ''
    
    return userName, machine, email

#==============================================================================

class ConsoleColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BLUE = "\033[1;34m"
    CYAN = "\033[1;36m"
    GREEN = "\033[0;32m"
    MAGENTA = '\033[0;35m'

#=============================================================================

def initiateLogging(parentApplication=None, level=logging.DEBUG):
    
    userHome = os.path.join(os.path.expanduser('~'), '.queueApp')
    
    if not os.path.exists(userHome):
        os.makedirs(userHome)
    
    logging.basicConfig(
        filename=os.path.join(userHome, LOG_FILE),
        format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p',
        level=logging.DEBUG)
    
    revision, modifiedBy, lastModified = getVersionInfo()
    userName, machine, email = getUserInfo()
    
    logging.info(40*'#')
    if parentApplication is not None:
        logging.info('%s started' % parentApplication.APPLICATION_NAME)
        logging.info('Revision: %s' % revision)
        logging.info('User:     %s' % userName)
        logging.info('Machine:  %s' % machine)
        logging.info(40*'#')
    
    rootLogger = logging.getLogger()
    
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logging.Formatter('\t%(message)s'))
    consoleHandler.setLevel(level)
    rootLogger.addHandler(consoleHandler)
    
    
        
#==============================================================================
