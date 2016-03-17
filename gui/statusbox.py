'''
@packge statusbox This package includes a box that can be included inside a
gui. It provides a visual display to show, warnings and status messages
to the user.
'''

from PyQt4 import QtGui
from PyQt4.QtGui import QIcon
from statusmessage import *

class StatusBoxMessage(QtGui.QListWidgetItem):
    '''
    \brief a message in a StatusBox, that gives a clue about
    what is going on in the background

    This message contains a picture that signals a
    warning or an error and a status. If the status
    does not contain a warning or error nog picture is presented
    '''
    WARN = "images/warning.svg"
    ERROR= "images/error.svg"

    def __init__(self, msg, parent=None):
        if msg.get_status() == StatusMessage.warning:
            super(StatusBoxMessage, self).__init__(QIcon(self.WARN), str(msg), parent)
        elif msg.get_status() == StatusMessage.error:
            super(StatusBoxMessage, self).__init__(QIcon(self.ERROR), str(msg), parent)
        else:
            super(StatusBoxMessage, self).__init__(str(msg), parent)

class StatusBox (QtGui.QListWidget):
    '''
    \brief Instances of this class show statusmessages
    about the program

    A status box is a small widget that has a few
    lines. on each line is a status message printed.
    The status informs the user about what is happening.
    '''

    def __init__(self, parent=None):
        super(StatusBox, self).__init__(parent)
        self.initFont();

    def initFont(self):
        font = QtGui.QFont("Monospace")
        font.setStyleHint(QtGui.QFont.TypeWriter)
        font.setPointSize(18.0/2)
        self.setFont(font)


    def addMessage(self, message):
        self.insertItem(0,StatusBoxMessage(message))
        
