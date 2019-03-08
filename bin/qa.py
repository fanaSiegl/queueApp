#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import traceback

import main as q 

#==============================================================================

def main():
        
    parser = argparse.ArgumentParser(description=q.__doc__[:q.__doc__.find('Usage')],
        formatter_class=argparse.RawDescriptionHelpFormatter)
#     parser.add_argument('-g', action='store_true', help='Run gui.')
    parser.add_argument('-inp', nargs=1, metavar='inp_path', dest='inpFilePath',
        help='ABAQUS Input file path.')
    parser.add_argument('-license',
        choices=[licenseServer.NAME for licenseServer in q.bi.LICENSE_SERVER_TYPES],
        help='ABAQUS license server type.')
    parser.add_argument('-solver', choices=q.ei.ABAQUS_SOLVER_LIST,
        help='ABAQUS solver version.')
    parser.add_argument('-host', choices=q.getListOfHosts(),
        help='Calculation host.')
    parser.add_argument('-cpu', nargs=1, help='Number of CPUs.')
    parser.add_argument('-gpu', nargs=1, help='Number of GPUs.')
    parser.add_argument('-prio', nargs=1, help='Job priority.')
    parser.add_argument('-start', nargs=1, help='Job start time.')
    parser.add_argument('-des', nargs=1, help='Job description (max. 15 characters).')
    parser.add_argument('-param', nargs=1, help='Additional ABAQUS parameters: "-x y -xx yy" (max 15 characters).')
    
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