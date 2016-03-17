#!/usr/bin/env python

'''
This file is the entry point for iSpector.
'''

from gui.ispectorgui import ISpectorGui
from gui.ispectorgui import MainGuiModel
import gui.statusmessage as sm
from gui.app import ISpectorApp
from PyQt4 import QtCore
import sys

def main():
    '''
    The iSpector main function
    '''

    import utils.arguments
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
