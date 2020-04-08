#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Python script for '''

import os
import sys

#==============================================================================

ALLOWED_PROJECT_PATHS = [
    '/data/fem', '/data/sk_1', '/data/sk_2', '/data/sk_3', '/data/vwg',
    '/data/bmw', '/data/fgs', '/data/simulia', '/data/ostatni',
    '/data/ostatni_2', '/data/bmw-br', '/data/epo-br']

META_POST_PROCESSING_PATH = '/data/fem/+software/SKRIPTY/tools/python/metaTools/SESSION'
META_EXECUTABLE = '/usr1/applications/ansa/BETA_CAE_Systems/meta_post_v19.1.1/meta_post64.sh'

#===============================================================================

USER = 0
EXPERT_USER = 1
ADMIN = 2

AUTHENTICATION = {
    'siegl' : ADMIN,
#     'siegl' : USER,
    'stekly': EXPERT_USER,
    'bouda' : EXPERT_USER,
    'marada' : EXPERT_USER,
    'cejpek' : EXPERT_USER,
    }

AUTHENTICATION_RULES = {
    USER : 'User',
    EXPERT_USER : 'Expert user',
    ADMIN : 'Admin'}

#==============================================================================

class SolverVersionException(Exception): pass

#==============================================================================

class AbaqusSolverVersions(object):
    
    SOLVER_LIST = ['abaqus6141', 'abaqus2016x', 'abaqus2017x',
        'abaqus2018x', 'abaqus2018-HF4', 'abaqus2019x']
    SOLVER_PATHS = {
        'abaqus6141' : 'abaqus6141',
        'abaqus2016x': 'abaqus2016x',
        'abaqus2017x': 'abaqus2017x',
        'abaqus2018x': 'abaqus2018x',
        'abaqus2018-HF4': 'abaqus2018-HF4',
        'abaqus2019x': 'abaqus2019x'}
    DFT_VERSION = 'abaqus2019x'
    
    #--------------------------------------------------------------------------
    @classmethod
    def getSolverPath(cls, version):
        
        if version not in cls.SOLVER_LIST:
            raise(SolverVersionException(
                '"%s" not found in available versions: %s' % (version, cls.SOLVER_LIST)))
        
        return cls.SOLVER_PATHS[version]
    
    #--------------------------------------------------------------------------
    @classmethod
    def getDftVersionIndex(cls):
        
        return cls.SOLVER_LIST.index(cls.DFT_VERSION) + 1
    

#==============================================================================

class PamcrashSolverVersions(AbaqusSolverVersions):
    
    SOLVER_LIST = [
        'PAMCRASH v2015.03',
        'PAMCRASH v2016.06']
    SOLVER_PATHS = {
        'PAMCRASH v2015.03' : '/usr1/applications/pamcrash/v2015.03/pamcrash_safe/2015.03/pamworld',
        'PAMCRASH v2016.06' : '/usr1/applications/pamcrash/v2016.06/pamcrash_safe/2016.06/pamworld'}
    DFT_VERSION = 'PAMCRASH v2015.03'

#==============================================================================

class NastranSolverVersions(AbaqusSolverVersions):
    
    SOLVER_LIST = [
        'NASTRAN nas20171']
    SOLVER_PATHS = {
        'NASTRAN nas20171' : '/usr/local/bin/nas20171'}
    DFT_VERSION = 'NASTRAN nas20171'

#==============================================================================

class ToscaSolverVersions(AbaqusSolverVersions):
    
    SOLVER_LIST = [
        'tosca19']
    SOLVER_PATHS = {
        'tosca19' : 'tosca19'}
    DFT_VERSION = 'tosca19'
    
#==============================================================================

class FileExtensions(object):
    
    ABAQUS_INPUT = '.inp'
    ABAQUS_RESTART = '.res'
    PAMCRASH_INPUT = '.pc'
    NASTRAN_INPUT = '.bdf'
    TOSCA_INPUT = '.par'

#==============================================================================

class AnalysisTypes(object):
    
    IMPLICIT = 'IMPLICIT'
    EXPLICIT = 'EXPLICIT'
    
    ABAQUS = []
    PAMCRASH = {
        'IMPLICIT' : IMPLICIT,
        'EXPLICIT' : EXPLICIT}


