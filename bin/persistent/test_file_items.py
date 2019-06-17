#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Python script for '''

import os
import sys
import unittest

from domain import utils
from domain import enum_items as ei

import file_items as fi

#==============================================================================

ABAQUS_INP_FILE_PATH = os.path.join(utils.PATH_RES, 'test_files', 'ABAQUS')
PAMCRASH_INP_FILE_PATH = os.path.join(utils.PATH_RES, 'test_files', 'PamCrash')
NASTRAN_INP_FILE_PATH = os.path.join(utils.PATH_RES, 'test_files', 'NASTRAN')
TOSCA_INP_FILE_PATH = os.path.join(utils.PATH_RES, 'test_files', 'TOSCA')

#==============================================================================

class TestAbaqusInpFile(unittest.TestCase):
    
    def setUp(self):
                
        pass
    
    #-------------------------------------------------------------------------
    
    def test_analyseContent(self):
        
        testInpFile = os.path.join(
            ABAQUS_INP_FILE_PATH, 'expl_modal_ams.inp')
        
        inputFile = fi.AbaqusInpFile(testInpFile)
        self.assertTrue(inputFile.stepPerturbation)
        self.assertTrue(inputFile.dynamicsExplicit)
        self.assertEqual(inputFile.eigSolver, 'AMS')
        
        
        testInpFile = os.path.join(
            ABAQUS_INP_FILE_PATH, 'stat_modal_lanczos.inp')
        
        inputFile = fi.AbaqusInpFile(testInpFile)
        self.assertFalse(inputFile.stepPerturbation)
        self.assertFalse(inputFile.dynamicsExplicit)
        self.assertEqual(inputFile.eigSolver, 'LANCZOS')
        
        
        testInpFile = os.path.join(
            ABAQUS_INP_FILE_PATH, 'modal_lanczos.inp')
        
        inputFile = fi.AbaqusInpFile(testInpFile)
        self.assertTrue(inputFile.stepPerturbation)
        self.assertFalse(inputFile.dynamicsExplicit)
        self.assertEqual(inputFile.eigSolver, 'LANCZOS')
        
        
        testInpFile = os.path.join(
            ABAQUS_INP_FILE_PATH, 'modal_ams.inp')
        
        inputFile = fi.AbaqusInpFile(testInpFile)
        self.assertTrue(inputFile.stepPerturbation)
        self.assertFalse(inputFile.dynamicsExplicit)
        self.assertEqual(inputFile.eigSolver, 'AMS')
        
        
        testInpFile = os.path.join(
            ABAQUS_INP_FILE_PATH, 'SK3165EUB_B-RB-NL_001_001_d60_500N_70C.inp')
        
        inputFile = fi.AbaqusInpFile(testInpFile)
        self.assertFalse(inputFile.stepPerturbation)
        self.assertFalse(inputFile.dynamicsExplicit)
        self.assertIsNone(inputFile.eigSolver)
        self.assertEqual(len(inputFile.includeFiles), 6)
        
    #-------------------------------------------------------------------------
    
    def test_analyseContentRestart(self):
        
        testInpFile = os.path.join(
            ABAQUS_INP_FILE_PATH, 'restart','w_skew_plate_linear.inp')
        inputFile = fi.AbaqusInpFile(testInpFile)
        self.assertTrue(inputFile.retAllFiles)
        self.assertFalse(inputFile.subAllFiles)
        
        testInpFile = os.path.join(
            ABAQUS_INP_FILE_PATH, 'restart','w_skew_plate_restart.inp')
        inputFile = fi.AbaqusInpFile(testInpFile)
        self.assertFalse(inputFile.retAllFiles)
        self.assertTrue(inputFile.subAllFiles)
        

#==============================================================================

class TestPamCrashInpFile(unittest.TestCase):
    
    def test_analyseContentIncludeFiles(self):
        
        testInpFile = os.path.join(
            PAMCRASH_INP_FILE_PATH, 'SK3165EUB_BIU_003_001_103_003_2015.pc')
        
        inputFile = fi.PamCrashInpFile(testInpFile)
        self.assertEqual(len(inputFile.includeFiles), 6)
        self.assertEqual(inputFile.analysisType, ei.AnalysisTypes.EXPLICIT)
    
    #-------------------------------------------------------------------------
    
    def test_checkTitleName(self):
        
        testInpFile = os.path.join(
            PAMCRASH_INP_FILE_PATH, 'SK3165EUB_BIU_003_001_103_003_2016.pc')
        
        self.assertRaises(fi.PamCrashInpFileException,
            lambda: fi.PamCrashInpFile(testInpFile))
        
    #-------------------------------------------------------------------------
    
    def test_dataCheck(self):
        
        testInpFile = os.path.join(
            PAMCRASH_INP_FILE_PATH, 'SK3165EUB_BIU_003_datacheck_003_2015.pc')
        
        inputFile = fi.PamCrashInpFile(testInpFile)
        self.assertTrue(inputFile.dataCheck)
        
        testInpFile = os.path.join(
            PAMCRASH_INP_FILE_PATH, 'SK3165EUB_BIU_003_001_103_003_2015.pc')
        
        inputFile = fi.PamCrashInpFile(testInpFile)
        self.assertFalse(inputFile.dataCheck)
    
    #-------------------------------------------------------------------------
    
    def test_dataCheckModeSwitch(self):
        
        testInpFile = os.path.join(
            PAMCRASH_INP_FILE_PATH, 'SK3165EUB_BIU_003_switch_003_2015.pc')
        
        inputFile = fi.PamCrashInpFile(testInpFile)
        self.assertTrue(inputFile.dataCheck)
        
        # switching off data check
        inputFile.switchDataCheckMode()
        
        inputFile = fi.PamCrashInpFile(testInpFile)
        self.assertFalse(inputFile.dataCheck)
        
        # switching on data check
        inputFile.switchDataCheckMode()
        
        inputFile = fi.PamCrashInpFile(testInpFile)
        self.assertTrue(inputFile.dataCheck)
        
#==============================================================================

class TestNastranInpFile(unittest.TestCase):
    
    def test_analyseContentIncludeFiles(self):
        
        testInpFile = os.path.join(
            NASTRAN_INP_FILE_PATH, 'LEAF-JPN_VC_NCAP-NVH_BENDING_001_04.bdf')
        
        inputFile = fi.NastranInpFile(testInpFile)
        self.assertEqual(len(inputFile.includeFiles), 1)        
        self.assertEqual(inputFile.includeFiles[0], 'LEAF-NVH_no_axes_01.inc')
        
        testInpFile = os.path.join(NASTRAN_INP_FILE_PATH,
            'LEAF-JPN_VC_NCAP-NVH_BENDING_001_05_missing_include.bdf')
        self.assertRaises(fi.InpFileException,
            lambda: fi.NastranInpFile(testInpFile))


#==============================================================================

class TestToscaInpFile(unittest.TestCase):
    
    def test_analyseContentIncludeFiles(self):
        
        testInpFile = os.path.join(
            TOSCA_INP_FILE_PATH, 'control_arm_topo_controller_casting_01.par')
        
        inputFile = fi.ToscaInpFile(testInpFile)
        self.assertEqual(len(inputFile.includeFiles), 1)        
        self.assertEqual(inputFile.includeFiles[0], 'control_arm_whole.inp')
                
#==============================================================================
