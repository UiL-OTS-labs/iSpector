#!/usr/bin/env python

##
# \file statusbox.py This file includes a box that can be included inside a
# gui. It provides a visual display to show, warnings and status messages
# to the user.

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QIcon
from .statusmessage import StatusMessage


class StatusBoxMessage(QtWidgets.QListWidgetItem):
    '''
    A message in a StatusBox, that gives a clue about
    what is going on in the background

    This message contains a picture that signals a
    warning or an error and a status. If the status
    does not contain a warning or error no picture is presented.
    '''

    ## filename of the warning icon
    WARN = "images/warning.svg"
    ## filename of the error icon
    ERROR = "images/error.svg"

    ##
    # inits a new StatusBoxMessage
    #
    # \param msg, a statusmessage.StatusMessage
    # \param parent the parent window or None.
    def __init__(self, msg, parent=None):
        if msg.get_status() == StatusMessage.warning:
            super().__init__(QIcon(self.WARN), str(msg), parent)
        elif msg.get_status() == StatusMessage.error:
            super().__init__(QIcon(self.ERROR), str(msg), parent)
        else:
            super().__init__(str(msg), parent)


##
# Instances of this class show statusmessages
# about the program
#
# A status box is a small widget that has a few
# lines. on each line is a status message printed.
# The status informs the user about what is happening.
#
class StatusBox (QtWidgets.QListWidget):

    ## construct a statusbox
    def __init__(self, parent=None):
        super(StatusBox, self).__init__(parent)
        self._initFont()

    ## intializes the font of the box.
    def _initFont(self):
        font = QtGui.QFont("Monospace")
        font.setStyleHint(QtGui.QFont.TypeWriter)
        font.setPointSize(18 // 2)
        self.setFont(font)

    ## Add a new message to the box
    # @param message an instance of StatusMessage
    def addMessage(self, message):
        self.insertItem(0, StatusBoxMessage(message))
        
