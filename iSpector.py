#!/usr/bin/env python3

##
# \file iSpector.py The entry point for iSpector
#

##
# \mainpage
# \author Maarten Duijndam
#
# \section License
# GPL version 2 (see LICENSE in the source root)
#
# \section Introduction
#
# iSpector reads logfiles by experimentation programs. The logfiles must
# be formatted in such way that iSpector can understand what has happened.
# iSpector will than be able to read in the data of an experiment and
# will be able to separate the trials. Then it is possible to inspect
# the eyemovement signals. If the eyetracker doesn't report fixations
# and saccades or does so poorly, then iSpector can create them from
# the eyesignal.
#
# \section Future
# iSpector has continued to grow and will soon be able to do
# more suffisticated eye movement analysis. There is planned support
# for Reading and VisualWorld experiments. In the near future iSpector
# is also hooked up to libeye. That library makes it easy to use
# the library in new experiments written in an other language. And
# although the library is written in C++ a python interface is provided.
#
# \section History
# The development of iSpector is started at UiL-OTS a linguistics laboratry
# of Utrecht University in the Netherlands.
#
# It was orignally used to convert output of an SMI EyeTracker with the 
# <a href="http://www.beexy.org">Zep</a> experimentation tool to an output
# that is similar to the ascii files of an Eyelink eyetracker. We were not
# statisfied with the fixations as detected by the SMI eyetracker, so we
# decided to detect them ourselves.

import utils.arguments
from gui.ispectorgui import ISpectorGui
from gui.ispectorgui import MainGuiModel
import gui.statusmessage as sm
from gui.app import ISpectorApp
from PyQt5 import QtCore
import sys

def main():
    '''
    The iSpector main function
    '''

    QtCore.pyqtRemoveInputHook()
    un_parsed_args = utils.arguments.parseCmdLineKnown()
    app = ISpectorApp(un_parsed_args)
        
    #just keep looks inherited from the environment
    #app.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
    #app.setStyle(QtGui.QStyleFactory.create('windows'))
    #app.setStyle(QtGui.QStyleFactory.create('motif'))
    #app.setStyle(QtGui.QStyleFactory.create('macintosh'))

    winmodel = MainGuiModel(utils.arguments.ARGS)

    win = ISpectorGui(winmodel)
    win.reportStatus(sm.StatusMessage.ok, "iSpector started")
    if not winmodel.readConfig():
        win.reportStatus(sm.StatusMessage.warning, "Unable to read config file")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

