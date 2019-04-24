#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Python script for '''

import os
import sys

#==============================================================================

ABAQUS_SOLVER_LIST = ['abaqus6141', 'abaqus2016x', 'abaqus2017x',
        'abaqus2018x', 'abaqus2018-HF4', 'abaqus2019x']
ALLOWED_PROJECT_PATHS = [
    '/data/fem', '/data/sk_1', '/data/sk_2', '/data/vwg', '/data/bmw', '/data/fgs', '/data/simulia', '/data/ostatni', '/data/ostatni_2']
PAMCRASH_SOLVER_LIST = ['/usr1/applications/pamcrash/v2015.03/pamcrash_safe/', ]

#==============================================================================

class FileExtensions(object):
    
    ABAQUS_INPUT = '.inp'
    PAMCRASH_INPUT = '.pc'

#==============================================================================

class AnalysisTypes(object):
    
    IMPLICIT = 'IMPLICIT'
    EXPLICIT = 'EXPLICIT'
    
    ABAQUS = []
    PAMCRASH = {
        'IMPLICIT' : IMPLICIT,
        'EXPLICIT' : EXPLICIT}