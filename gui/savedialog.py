#!/usr/bin/env python

from PyQt5 import QtWidgets
from PyQt5 import QtCore

class SaveDialog (QtWidgets.QMessageBox):
    
    _msg     = ("You have made modifications, "
                "would you like to save the experiment?"
                )
    _title   = "Save Experiment"
    _present_buttons = QtWidgets.QMessageBox.Save |     \
                       QtWidgets.QMessageBox.Discard |  \
                       QtWidgets.QMessageBox.Cancel
    
    def __init__(self):
        super(SaveDialog, self).__init__()
        self.setText(self._title)
        self.setInformativeText(self._msg)
        self.setStandardButtons(self._present_buttons)
        self.setDefaultButton(self.Save)
        self.setIcon(self.Information)

