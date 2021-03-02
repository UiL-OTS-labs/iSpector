#!/usr/bin/env python

##
# \file configfile.py
# configfile.py contains methods to save a config file for the current
# user

import json
import sys
import os.path

##
# Our name
PROGRAM     = "iSpector"
##
# extension for a configuration file
EXTENSION   = ".json"
##
# contains the directory where the configfile should be stored.
DIR         = "dir"

##
# a constant uset to obtain the recently used files from the config
FILE_HIST   = "file_hist"

##
# Name of config dir under linux / unix
UNIX_CONFIG_DIR = ".config"

##
# constants used inside the json for the groups.
STIMDIR     = "stimdir"
FILEDIR     = "filedir"
OUTPUTDIR   = "outputdir"

##
# This is the representation of the directories used by iSpector
#
# The config dir stores all the directories that are special to iSpector.
class ConfigDir(dict):

    ##
    # initalizes a ConfigDir
    def __init__(self, stimdir="", filedir="", outputdir=""):
        self[STIMDIR]     = stimdir
        self[FILEDIR]     = filedir
        self[OUTPUTDIR]   = outputdir

##
# This is a representation of configuration used by iSpector
class ConfigFile (dict):
    
    ##
    # name of environmental variable that may hold the location where 
    # configuration data is stored.
    # https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
    # 2019
    XDG_CONFIG_HOME = "XDG_CONFIG_HOME"

    ##
    # Opens the config file, or creates it when it does not exists
    def __init__(self):
        
        ## the location in the file system for the configuration file
        self.configdir = self._tryToFindConfigDir()
        ## name for the configuration file.
        self.conffile  = self.configdir + PROGRAM + EXTENSION
        if not os.path.exists(self.conffile):
            self.create()
        try :
            self.parse()
        except json.decoder.JSONDecodeError as e:
            msg = "Unable to parse configfile {} because: {}".format(
                self.conffile,
                str(e)
            )
            print(msg, file=sys.stderr)
            print("Creating a new one...", file=sys.stderr)
            self.create()

    ##
    # Writes itself to the config file.
    def write(self):
        f = open(self.conffile, 'w')
        f.write(json.dumps(self, indent=4))
        f.close()

    ##
    # parses itself
    def parse(self):
        with open(self.conffile, 'r') as f:
            content = f.read()
            self.update(json.loads(content))

    ##
    # \brief Creates the directory and path to a in the file system
    # json config file
    def create(self):
        if not os.path.exists(self.configdir):
            os.makedirs(self.configdir)
        with open(self.conffile, 'w') as f:
            self[DIR] = ConfigDir()
            self[FILE_HIST] = list()

            f.write(json.dumps(self))

    ##
    # \brief Return the path to the config directory of iSpector
    #
    # Tries to examine the APPDATA global variable.
    # otherwise it tries to find the value for the HOME file
    # and uses that as base path
    #
    # \return APPDATA or HOME folder + iSpector
    def _getWindowsConfigDir(self):
        path = os.getenv('APPDATA')
        if not path:
            path = os.path.expanduser('~/' + PROGRAM + '/')
        else:
            path += "/" + PROGRAM + "/"
        return path
    
    ##
    # returns the unix configuration directory.
    # \return a path to a unix config dir.
    def _getUnixConfigDir(self):
        path = os.getenv(self.XDG_CONFIG_HOME)
        if path:
            return path + PROGRAM + "/"

        return os.path.expanduser("~/" + UNIX_CONFIG_DIR + "/" + PROGRAM + "/")

    ##
    # Tries to find the $HOME under unices, but appdata under windows.
    #
    def _tryToFindConfigDir(self):
        path = ""
        if sys.platform == "win32":
            path = self._getWindowsConfigDir()
        else:
            path += self._getUnixConfigDir()
        return path


if __name__ == "__main__":
    conffile = ConfigFile()
    conffile.write()
    print(json.dumps(conffile, indent=2))

