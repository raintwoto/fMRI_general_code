#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  2 22:53:58 2017

@author: biahan
"""
import subprocess

for i in range(14177244,14177244+53):
    cmdline="qdel "+str(i)
    try:
        subprocess.call(cmdline,shell=True)
    
    except subprocess.CalledProcessError:
        pass # handle errors in the called executable
    except OSError:
        pass # executable not found
