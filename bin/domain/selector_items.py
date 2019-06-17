#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Python script for '''

import os
import sys
import glob
import time
import logging

import utils
import enum_items as ei
import base_items as bi

#==============================================================================

class DataSelectorException(Exception): pass

#==============================================================================

class BaseDataSelector(object):
    
    DFT_OPTION_INDEX = 1
    DESCRIPTION = ''
    
    #-------------------------------------------------------------------------
    
    def __init__(self, parentApplication):
         
        self.parentApplication = parentApplication
    
    #-------------------------------------------------------------------------
    @staticmethod
    def printSelectionTitle(title):
        
        LENGTH = 80
        
        separator = '-'*((LENGTH - len(title) - 2)/2)
        additionalCharacter = (LENGTH - len(title) - 2) % 2
        
        print '%s %s %s' % (separator, title, separator + additionalCharacter*'-')
    
    #-------------------------------------------------------------------------
    
    def _getOptionFromList(self, description, prompt, options, multiSelection=False):
        
        # show message
        self.printSelectionTitle(description)
        
        optionNos = list()
        for iNo, option in enumerate(options):
            line = '{:>2}. {:}'.format(iNo + 1, option)
            # highlight default option
            if iNo + 1 == self.DFT_OPTION_INDEX:
                line = utils.ConsoleColors.OKGREEN + line + utils.ConsoleColors.ENDC
            
            print line
            optionNos.append(iNo + 1)
                        
        index = raw_input(prompt)
        
        if len(index) == 0:
            if multiSelection:
                return [self.DFT_OPTION_INDEX - 1, ]
            else:
                return self.DFT_OPTION_INDEX - 1
        
        try:
            # treat multi-selection option - must return a list
            if multiSelection:
                if index == 'a':
                    return [int(option) - 1 for option in optionNos]
                
                partsSpace = index.split(' ')
                partsComma = index.split(',')
                if partsSpace > 0 and len(partsSpace) > 1:
#                     print 'space sep', partsSpace
                    indexes = list()
                    for part in partsSpace:
                        # test for index error
                        option = options[int(part) - 1]
                        indexes.append(int(part) - 1)
                    return indexes
                elif partsComma > 0 and len(partsComma) > 1:
#                     print 'comma sep', partsComma
                    indexes = list()
                    for part in partsComma:
                        # test for index error
                        option = options[int(part) - 1]
                        indexes.append(int(part) - 1)
                    return indexes
                else:
#                     print 'other "%s"' % index
                    # prevent an 0. option
                    if int(index) == 0:
                        raise DataSelectorException()
                    
                    # test for index error
                    option = options[int(index) - 1]
                    return [int(index) - 1, ]
                
            # prevent an 0. option
            if int(index) == 0:
                index = None
            
            # test for index error
            option = options[int(index) - 1]
            
            return int(index) - 1
        except Exception as e:
            print '\tNot valid option: %s' % index
            print '\tPlease select one of numbers: %s' % optionNos
            
            return self._getOptionFromList(description, prompt, options, multiSelection)
    
    #-------------------------------------------------------------------------
    
    def getSelection(self):
        
        return
    
    #-------------------------------------------------------------------------
    
    def getOptions(self):
        
        return list()
    
    #--------------------------------------------------------------------------
    
    def indexToItem(self, index):
        
        return index
    
    #-------------------------------------------------------------------------
    @staticmethod
    def getTextInput(prompt, dftValue):
        
        text = raw_input(prompt)
        
        if len(text) == 0:
            return dftValue
        
        return text
    
    #-------------------------------------------------------------------------
    @classmethod
    def getTimeInput(cls, prompt, dftValue):
        
        text = raw_input(prompt)
        
        if len(text) == 0:
            return dftValue
        
        try:
            timeObject = time.strptime(text, '%m%d%H%M')
            timeString = time.strftime('%m%d%H%M', timeObject)
            
            return timeString
        
        except Exception as e:
            print '\tNot valid time format!'
            print '\tPlease provide time in a format: MMDDhhmm'
            
            return cls.getTimeInput(prompt, dftValue)        
        
    #-------------------------------------------------------------------------
    @classmethod
    def getIntInput(cls, description, prompt, minValue=0, maxValue=10, dftValue=5):
        
        # show message
        cls.printSelectionTitle(description)
                                
        value = raw_input(prompt)
        
        if len(value) == 0:
            return dftValue
        
        try:
            value = int(value)
            
            if value >= minValue and value <= maxValue:                                    
                return value
            else:
                raise DataSelectorException('Value out of range.')
            
        except Exception as e:
            print '\tNot valid value: %s' % value
            print '\tPlease select a number between %s and %s' % (minValue, maxValue)
            
            return cls.getIntInput(description, prompt, minValue, maxValue, dftValue)
        
        
#==============================================================================

class LicenseServerSelector(BaseDataSelector):
    
    DFT_OPTION_INDEX = 1
    DESCRIPTION = 'Available license servers'
    
    #-------------------------------------------------------------------------
    
    def getOptions(self):
        
        options = list()
        for licenseServer in bi.LICENSE_SERVER_TYPES[:3]:   
            options.append(licenseServer.toOptionLine())
        
        return options
    
    #--------------------------------------------------------------------------
    
    def indexToItem(self, index):
#         
#         licenseServerList = self.getOptions()
        
        return bi.LICENSE_SERVER_TYPES[:3][index]
    
    #-------------------------------------------------------------------------
    
    def getSelection(self):
        
        options = self.getOptions()
#         licenseServerList = self.getOptions()
#         
#         options = list()
#         for licenseServer in licenseServerList:
#             status = licenseServer.getTokenStatus()
#             options.append('%s %s license (free tokens: %s/%s)' % (
#                 licenseServer.LICENSE_TYPE.NAME, licenseServer.NAME, status['free'], status['total']))
                        
        # print list of servers
        index = self._getOptionFromList(
            self.DESCRIPTION,
            "Enter the number which represent ABAQUS queue [enter=%s]: " % self.DFT_OPTION_INDEX,
            options)
        
        return self.indexToItem(index)
    
#==============================================================================

class InputFileSelector(BaseDataSelector):
    
    FILE_EXT = ei.FileExtensions.ABAQUS_INPUT

#     def __init__(self, parentApplication):
#          
#         self.parentApplication = parentApplication
#         
#         # this is static to prevent content change in the middle of application run
#         self.filesList = glob.glob(os.path.join(
#             self.parentApplication.getWorkDir(), '*%s' % self.FILE_EXT))
            
    #--------------------------------------------------------------------------

    def getOptions(self):
        
        return glob.glob(os.path.join(self.parentApplication.getWorkDir(), '*%s' % self.FILE_EXT))
    
    #--------------------------------------------------------------------------
    
    def indexToItem(self, indexes):
        
        inpFiles = self.getOptions()
        
        return [inpFiles[index] for index in indexes]
    
    #--------------------------------------------------------------------------

    def getSelection(self):
        
        inpFiles = self.getOptions()
        
        # select input file
        if len(inpFiles) == 0:
            logging.error("Error: source *%s wasn't found!" % self.FILE_EXT)
            raise DataSelectorException("Error: source *%s wasn't found!" % self.FILE_EXT)
        elif len(inpFiles) == 1:
            return inpFiles
        else:
            indexes = self._getOptionFromList('Available input files',
                'Select input file(s) No. [1 or 1 2 ..., enter=%s, a=all]: ' % self.DFT_OPTION_INDEX,
                [os.path.basename(inpFileName) for inpFileName in inpFiles],
                multiSelection=True)
            
            return self.indexToItem(indexes)
            
#==============================================================================

class RestartInputFileSelector(InputFileSelector):
            
    def getSelection(self):
        
        inpFiles = self.getOptions()
        
        # select input file
        if len(inpFiles) == 0:
            raise DataSelectorException("Error: source *%s wasn't found!" % self.FILE_EXT)
        elif len(inpFiles) == 1:
            return inpFiles
        else:
            index = self._getOptionFromList('Available input files for restart',
                'Select input file No. [enter=%s]: ' % self.DFT_OPTION_INDEX,
                [os.path.basename(inpFileName) for inpFileName in inpFiles])
            
            return inpFiles[index]
    
#==============================================================================

class SolverVersionSelector(BaseDataSelector):
    
    DFT_OPTION_INDEX = ei.AbaqusSolverVersions.getDftVersionIndex()
    DESCRIPTION = 'Choose the ABAQUS solver version'
    VERSIONS = ei.AbaqusSolverVersions
      
    #--------------------------------------------------------------------------
    
    def getOptions(self):

#TODO: load dynamically?
        
        versions = self.VERSIONS.SOLVER_LIST
        
        return versions
    
    #--------------------------------------------------------------------------

    def getSelection(self):
        
        options = self.getOptions()
        
        index = self._getOptionFromList(
            self.DESCRIPTION,
            'Enter number which represent version of solver[enter=%s]: ' % self.DFT_OPTION_INDEX,
            options)
            
        return options[index]
    
    #--------------------------------------------------------------------------
    
    def indexToItem(self, index):
         
        versions = self.getOptions()
#         return versions[index]
        
        return self.VERSIONS.getSolverPath(versions[index])
    
#==============================================================================

class ExecutionServerSelector(BaseDataSelector):
    
    DFT_OPTION_INDEX = 2
    DESCRIPTION = 'Choose the execution host'
    
    #--------------------------------------------------------------------------
    
    def getOptions(self):
        
#         hosts = self.parentApplication.profile.jobSettings.licenseServer.getAvailableHosts()
#         
#         # sort servers and user workstations
#         allHosts = list()
#         userHosts = list()
#         serverHosts = list()
#         for host in hosts:
#             if type(host) is WorkstationExecutionServerType:
#                 userHosts.append(host)
#             else:
#                 serverHosts.append(host)
        
        licenseServer = self.parentApplication.profile.jobSettings.licenseServer
        
        allHosts = list()
        userHosts = licenseServer.getWorkstations()
        serverHosts = licenseServer.getAPservers()
        
        allHosts.extend(serverHosts)
        allHosts.extend(userHosts)
        
        infoLines = list()
        for host in allHosts:
            infoLine = host.getInfoLine(licenseServer.CODE)
            infoLines.append(infoLine)
        
        # server type overview  
        description = 'Info - your computer is: %s' % self.parentApplication.profile.user.machine      
        for server in serverHosts:
            description += '\n\t%s (%s cores, %s GPU, %s, free cores: %s)' % (
                server.NAME, server.NO_OF_CORES, server.NO_OF_GPU, server.DESCRIPTION,
                server.freeCpuNo)
#             description += '\n\t' + server.getDescription()
                
        description += '\n\t%s' % bi.WorkstationExecutionServerType.getDescription()
        
        return allHosts, infoLines, serverHosts, userHosts, description
    
    #--------------------------------------------------------------------------

    def getSelection(self):
        
        hosts, infoLines, serverHosts, userHosts, description = self.getOptions()
        
        description += '\nAvailable execution hosts for this queue'
        description += '\n' + 80*'-'
        description += '\nqueuename                      qtype resv/used/tot. load_avg    arch       states'
        description += '\n' + 80*'-'
        
        # highlight user machine   
        for optionIndex, host in enumerate(hosts):
            if host.isUserMachine:
                infoLine = infoLines[optionIndex]
                infoLines[optionIndex] = utils.ConsoleColors.OKBLUE + infoLine + utils.ConsoleColors.ENDC
        
        self.printSelectionTitle(self.DESCRIPTION)
        
        index = self._getOptionFromList(description, 
            "Enter the number which represent preferred execution host [enter=%s]: " % self.DFT_OPTION_INDEX,
            infoLines)
                        
        return hosts[index]
    
    #--------------------------------------------------------------------------
    
    def indexToItem(self, index):
        
        hosts, infoLines, serverHosts, userHosts, description = self.getOptions()
        
        return hosts[index]

#==============================================================================

class PamcrashInputFileSelector(InputFileSelector):
    
    FILE_EXT = ei.FileExtensions.PAMCRASH_INPUT
    
#==============================================================================

class PamCrashExecutionServerSelector(ExecutionServerSelector):
    
    DFT_OPTION_INDEX = 1

#==============================================================================

class PamCrashLicenseServerSelector(LicenseServerSelector):
    
    DFT_OPTION_INDEX = 1
    DESCRIPTION = 'Available license servers'
    
    #-------------------------------------------------------------------------
    
    def getOptions(self):
        
        return [bi.LICENSE_SERVER_TYPES[3].toOptionLine()]
    
    #--------------------------------------------------------------------------
    
    def indexToItem(self, index):
        
        return bi.LICENSE_SERVER_TYPES[3]

#==============================================================================

class PamCrashSolverVersionSelector(SolverVersionSelector):
    
    DFT_OPTION_INDEX = ei.PamcrashSolverVersions.getDftVersionIndex()
    DESCRIPTION = 'Choose the PamCrash solver version'
    VERSIONS = ei.PamcrashSolverVersions            

#==============================================================================

class NastranInputFileSelector(InputFileSelector):
    
    FILE_EXT = ei.FileExtensions.NASTRAN_INPUT

#==============================================================================

class NastranLicenseServerSelector(LicenseServerSelector):
    
    DFT_OPTION_INDEX = 1
    DESCRIPTION = 'Available license servers'
    
    #-------------------------------------------------------------------------
    
    def getOptions(self):
        
        return [bi.LICENSE_SERVER_TYPES[4].toOptionLine()]
    
    #--------------------------------------------------------------------------
    
    def indexToItem(self, index):
        
        return bi.LICENSE_SERVER_TYPES[4]
    
#==============================================================================

class NastranSolverVersionSelector(SolverVersionSelector):
    
    DFT_OPTION_INDEX = ei.NastranSolverVersions.getDftVersionIndex()
    DESCRIPTION = 'Choose the Nastran solver version'
    VERSIONS = ei.NastranSolverVersions   

#==============================================================================

class NastranExecutionServerSelector(ExecutionServerSelector):
    
    DFT_OPTION_INDEX = 1

#==============================================================================

class ToscaInputFileSelector(InputFileSelector):
    
    FILE_EXT = ei.FileExtensions.TOSCA_INPUT

#==============================================================================

class ToscaSolverVersionSelector(SolverVersionSelector):
    
    DFT_OPTION_INDEX = ei.ToscaSolverVersions.getDftVersionIndex()
    DESCRIPTION = 'Choose the Tosca solver version'
    VERSIONS = ei.ToscaSolverVersions  
    
#==============================================================================

class PostProcessingSelector(BaseDataSelector):
    
    DFT_OPTION_INDEX = 1
    DESCRIPTION = 'Available post-processing options'
    
    #-------------------------------------------------------------------------
    
    def _getPostProcessingTypes(self):
        
        solverType = self.parentApplication.profile.job.SOLVER_TYPE
        
        postProcessingTypes = list()
        postProcessingTypes.extend(bi.POST_PROCESSING_TYPES)#[:2])
        postProcessingTypes.extend(solverType.POST_PROCESSING_TYPES)
#         postProcessingTypes.extend(bi.POST_PROCESSING_TYPES[2:])
                
        return postProcessingTypes
        
    #-------------------------------------------------------------------------
    
    def getOptions(self):
              
        postProcessingTypes = self._getPostProcessingTypes()
        
        options = list()
        for postProcessingOption in postProcessingTypes:   
            options.append(postProcessingOption.NAME)
        
        return options
    
    #--------------------------------------------------------------------------
    
    def indexToItem(self, index):
        
        postProcessingTypes = self._getPostProcessingTypes()
                
        return postProcessingTypes[index]
    
    #-------------------------------------------------------------------------
    
    def getSelection(self):
        
        options = self.getOptions()
                    
        # print list of servers
        index = self._getOptionFromList(
            self.DESCRIPTION,
            "Enter the number which represents a post-processing type [enter=%s]: " % self.DFT_OPTION_INDEX,
            options)
        
        return self.indexToItem(index)


    
        
        