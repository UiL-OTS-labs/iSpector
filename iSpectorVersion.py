#!/usr/bin/env python

'''
This file should not be editted by hand. Typically it is modified by using the
'bump-version.py' script. It reflects the build version of eye spector. The
minor version number should be odd for nightly build and even for stable builds.
'''

name = "iSpector"

iSpector_major = 0
iSpector_minor = 5
iSpector_micro = 1

def getVersionMajor():
    return iSpector_major

def getVersionMinor():
    return iSpector_minor

def getVersionMicro():
    return iSpector_micro

def getVersion():
    return name + "-" + str(iSpector_major) + "." +         \
            str(iSpector_minor) + "." + str(iSpector_micro)
