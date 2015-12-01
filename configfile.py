#!/usr/bin/env python

import json
import sys
import os.path

PROGRAM     = "iSpector"
EXTENSION   = ".json"
DIR         = "dir"

class ConfigDir(dict):
    '''
    This is the representation of the directories used by iSpector
    '''
    def __init__(self, stimdir="", filedir="", outputdir=""):
        self["stimdir"]     = stimdir
        self["filedir"]     = filedir
        self["outputdir"]   = outputdir

class ConfigFile (dict):
    '''
    This is a representation of configuration used by iSpector
    '''

    def __init__(self):
        '''
        opens the config file, or creates it when it does not exists
        '''
        self.configdir = self._tryToFindConfigDir()
        self.conffile  = self.configdir + PROGRAM + EXTENSION
        if not os.path.exists(self.conffile):
            self.create()
        self.parse()

    def write(self):
        '''
        Writes itself to the config file.
        '''
        f = open(self.conffile, 'w')
        f.write(json.dumps(self, indent=4))

    def parse(self):
        '''
        parses itself
        '''
        f = open(self.conffile, 'r')
        content = f.read()
        print content
        self = json.loads(content)

    def create(self):
        '''
        \brief Creates the directory and path to a in the file system
        json config file
        '''
        f = None
        if not os.path.exists (self.configdir):
            os.makedirs(self.configdir)
        if not os.path.exists(self.conffile):
            f = open(self.conffile, 'w')
        else :
            f = open(self.conffile, 'w')
        self[DIR] = ConfigDir()

        f.write(json.dumps(self))
        f.close()

    def get_dirs(self):
        '''
        \Obtains the directories from the config file
        '''
        json.dumps(self)

    def _getWindowsConfigDir(self):
        '''
        \brief Return the path to the config directory of iSpector

        Tries to examine the APPDATA global variable.
        otherwise it tries to find the value for the HOME file
        and uses that as base path

        \return APPDATA or HOME folder + iSpector
        '''
        path = os.getenv('APPDATA')
        if not path:
            path = os.path.expanduser('~/' + PROGRAM + '/')
        else:
            path += "/" + PROGRAM + "/"
        return path
    
    def _getUnixConfigDir(self):
        '''
        return $HOME/.iSpector
        '''
        return os.path.expanduser("~/.iSpector/")

    def _tryToFindConfigDir(self):
        '''
        Tries to find the $HOME under unices, but appdata under windows.
        '''
        path = ""
        if sys.platform == "win32":
            path = self._getWindowsConfigDir()
        else:
            path += self._getUnixConfigDir()
        return path


if __name__ == "__main__":
    conffile = ConfigFile()
    conffile.write()
    json.dumps(conffile, indent=2)

