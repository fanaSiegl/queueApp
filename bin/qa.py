#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
qa
==

submits ABAQUS job to Grid Engine

'''

import os
import sys
import time
import argparse
import traceback

import main as q 

#==============================================================================

def getListOfHosts():
    
    # initiate resource status
    q.ci.Resources.initialise()
    
    hosts = list()
    for licenseServer in getListLicenses()[1]:
        hosts.extend(
            [currentHost.name for currentHost in licenseServer.getAvailableHosts()])
    
    return sorted(set(hosts))

#==============================================================================

def getListLicenses():
    
    licenseNames = list()
    licenseServers = list()
    for licenseServer in q.bi.LICENSE_SERVER_TYPES:
        if 'abaqus' in licenseServer.CODE:
            licenseNames.append(licenseServer.NAME)
            licenseServers.append(licenseServer)
    
    return licenseNames, licenseServers
    
#==============================================================================

def main():
        
    parser = argparse.ArgumentParser(
        description=q.__doc__[:q.__doc__.find('Usage')] + __doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
#     parser.add_argument('-g', action='store_true', help='Run gui.')
    parser.add_argument('-inp', nargs='*', metavar='inp_path', dest='inpFilePath',
        help='ABAQUS Input file path.')
    parser.add_argument('-license',
        choices=getListLicenses()[0],
        default=getListLicenses()[0][q.bi.LicenseServerSelector.DFT_OPTION_INDEX - 1],
        help='ABAQUS license server type. (default=%s)' % [
            licenseServer.NAME for licenseServer in q.bi.LICENSE_SERVER_TYPES][q.bi.LicenseServerSelector.DFT_OPTION_INDEX - 1],)
    parser.add_argument('-solver', choices=q.ei.ABAQUS_SOLVER_LIST,
        default=q.ei.ABAQUS_SOLVER_LIST[q.bi.SolverVersionSelector.DFT_OPTION_INDEX - 1],
        help='ABAQUS solver version. (default=%s)' % q.ei.ABAQUS_SOLVER_LIST[
            q.bi.SolverVersionSelector.DFT_OPTION_INDEX - 1])
    parser.add_argument('-host', choices=getListOfHosts(), default='mb-so2',
        help='Calculation host. (default=mb-so2)')
    parser.add_argument('-cpu', default=4, type=int, help='Number of CPUs. (default=4)')
    parser.add_argument('-gpu', default=0, type=int, help='Number of GPUs. (default=0)')
    parser.add_argument('-prio', default=q.ci.AbaqusJob.DFT_PRIORITY, type=int,
        help='Job priority. (default=%s)' % q.ci.AbaqusJob.DFT_PRIORITY)
    parser.add_argument('-start', default=time.strftime('%m%d%H%M'),
        help='Job start time. (default=%s)' % time.strftime('%m%d%H%M'))
    parser.add_argument('-des', default='', help='Job description (max. 15 characters).')
    parser.add_argument('-param', default='', help='Additional ABAQUS parameters: "-x y -xx yy" (max 15 characters).')
    
    args = parser.parse_args()
        
    try:
        qaba = q.Qaba(args)
    except Exception as e:
        print str(e)
        if q.DEBUG:
            traceback.print_exc()
    
       
#==============================================================================

if __name__ == '__main__':
    main()