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
    
    def test_analyseContent_restart(self):
        
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
    
    def test_analyseContent_includeFiles(self):
        
        testInpFile = os.path.join(
            PAMCRASH_INP_FILE_PATH, 'SK3165EUB_BIU_003_001_103_003_2015.pc')
        
        inputFile = fi.PamCrashInpFile(testInpFile)
        self.assertEqual(len(inputFile.includeFiles), 6)
        self.assertEqual(inputFile.analysisType, ei.AnalysisTypes.EXPLICIT)
        
        
#==============================================================================
