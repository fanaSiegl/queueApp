#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import traceback

import main as q 

#==============================================================================

def main():
            
    try:
        queue = q.Queue()
    except Exception as e:
        print str(e)
        if q.DEBUG:
            traceback.print_exc()
    except KeyboardInterrupt:
        pass
    
#==============================================================================

if __name__ == '__main__':
    main()