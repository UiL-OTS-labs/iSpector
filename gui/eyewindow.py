#!/usr/bin/env python

## 
# \file eyewindow.py 
#


from PyQt5 import QtGui
from eyeoutputqt import ExamineDataModel

class EyeWindow (QtGui.QWidget):
    '''
    A standard window that provides a template for all kinds of operations.
    On one or multiple eyemovement files.
    '''

    def __init__(self, files, parent):
        super(EyeWindow, self).__init__(parent=parent, flags=QtCore.Qt.Window)
        self.MAINWINDOW = parent
        self.MODEL      = ExamineDataModel(files, parent)
        if not self.MODEL.eyedata:
            self.MAINWINDOW
            QtGui.QApplication.postEvent(self, QtGui.QCloseEvent())
            return
        self.controller = ExamineDataController(self.MODEL)
        self._initGui()
        self.updateFromModel()

    def _initGui(self):
        '''
        Adds all gui widgets and layout to it self.
        '''
        grid = QtGui.QGridLayout()
        tabview = QtGui.QTabWidget()
        self.tabview = tabview

        grid.addWidget(tabview, 0,0, 1, -1)

        button = QtGui.QPushButton('<-')
        button.setToolTip("Previouw trial")
        button.clicked.connect(self.prevTrial)
        grid.addWidget(button, 1,0)

        button = QtGui.QPushButton('->')
        button.setToolTip("Next trial")
        button.clicked.connect(self.nextTrial)
        grid.addWidget(button, 1, 3)

        self.fileslider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.fileslider.setMinimum(1)
        self.fileslider.setToolTip("File slider")
        self.trialslider= QtGui.QSlider(QtCore.Qt.Horizontal)
        self.trialslider.setMinimum(1)
        self.trialslider.setToolTip("Trial slider")
        
        self.fileslider.sliderReleased.connect(self.fileSliderChanged)
        self.trialslider.sliderReleased.connect(self.trialSliderChanged)
        
