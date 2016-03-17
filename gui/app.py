#!/usr/bin/env python

from PyQt4 import QtGui
from PyQt4 import QtCore

'''
This is the Qt application that runs the iSpector mainloop.
'''

class ISpectorApp(QtGui.QApplication):
    ''' Our own app mainly create to catch user events '''

    def notify(self, receiver, event):
        if event.type() > QtCore.QEvent.User:
            w = receiver
            while w:
                res = w.event(event)
                if res and event.isAccepted():
                    return res
                w = w.parent()
        return super(ISpectorApp, self).notify(receiver, event)

