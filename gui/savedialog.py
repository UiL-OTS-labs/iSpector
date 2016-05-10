#!/usr/bin/env python

from PyQt4 import QtGui
from PyQt4 import QtCore

class SaveDialog (QtGui.QMessageBox):
    
    _msg     = ("You have made modifications, "
                "would you like to save the experiment?"
                )
    _title   = "Save Experiment"
    _present_buttons = QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard
    
    def __init__(self):
        super(SaveDialog, self).__init__()
        self.setText(self._title)
        self.setInformativeText(self._msg)
        self.setStandardButtons(self._present_buttons)
        self.setDefaultButton(self.Save)
        self.setIcon(self.Information)

