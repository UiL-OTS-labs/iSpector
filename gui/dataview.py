#!/usr/bin/env python

##
# \file dataview.py
#
# This file contains the BaseClasses for viewing widgets
# in iSpector. The classes in this file should be used
# to derive dedicated viewers for special tasks related
# to eyetracking experiments.

from PyQt4 import QtGui
from PyQt4 import QtCore
import datamodel
import savedialog
import os

##
# CustomDataView
#
# CustomDataView shows one specific view on EyemovementData it is embedded
# inside a DataView.
class CustomDataView(object):
    
    ##
    # Lets the CustomDataView to update itself
    #
    # The CustomDataView has no idea what the Derived classes
    # want to show to the audience. Therefore the derived classes
    # should implement this function to update themselves after a
    # modification to the model.
    def updateFromModel(self):
        raise NotImplemented()


##
# DataView is a baseclass that helps viewing/editting one or multiple
# files.
#
# The DataView contains one special Widget that should be put there
# by a derived class. The special widget shows the relevant data of that
# trial or experiment.
#
class DataView(QtGui.QWidget):
    
    ##
    # inits a DataView
    #
    # \param [in] model an instance of the model this view is about to
    #             demonstrate
    # \param [in] controller a controller the view can uses to update the model.
    # \param [in] parent just passed to QWidget.__init__()
    # \param [in] flags the QtCore.Qt.WindowFlags
    def __init__(self, model, controller, parent=None, flags=QtCore.Qt.Window) :
        super(DataView, self).__init__(parent=parent, flags=flags)
        ## a reference to the main window
        self.MAINWINDOW     = parent
        ## the datamodel of this class
        self.MODEL          = model
        assert(isinstance(self.MODEL, datamodel.DataModel))
        ## the controller for updating the MODEL
        self.controller     = controller

        ## This widget will be placed in the top part of the view.
        self.custom_widget  = None

        # Add the custom widget as defined by derived class to the 
        self.initCustomWidget()
        assert(self.custom_widget != None)
        assert(isinstance(self.custom_widget, CustomDataView))

        # Make us know to the model, so the model also has an idea who it's
        # talking to.
        self.MODEL.setView(self)
        
        # initializes the gui
        self._initGui()

        # updates the entire view.
        self.updateFromModel()
    
    ##
    # initialize the custom widget.
    #
    # This method shall be instantiated by Classes derived from DataView.
    # after this method has been called self.custom_widget shall contain a
    # a initialized CustomDataView derived class.
    def initCustomWidget(self):
        msg = "Programming error: initCustomWidget called, it should be \
implemented in a derived class and do not call this widget's \
version."
        raise NotImplemented(msg)

    ##
    # A method that tests if the data is valid.
    #
    # Test whether the model has been loaded correctly. If the model wasn't
    # loaded correctly, then you will run into troubles. Therefore
    # you can abort the view with a usefull warning.
    #
    def hasValidData(self):
        return self.MODEL.hasValidData()

    ##
    # Adds all gui widgets and layout to it self.
    #
    # This function takes care of the basic layout of the DataView
    # It compasses a grid, which laysout a Widget at the top, that
    # uses the largest part of the window. Below there are one or two
    # sliders that allow the user to navigate throughout the trials and
    # files respectively.
    #
    def _initGui(self):
        grid = QtGui.QGridLayout()
        tabview = QtGui.QTabWidget()

        grid.addWidget(self.custom_widget, 0,0, 1, -1)

        button = QtGui.QPushButton('<-')
        button.setToolTip("Previous trial")
        button.clicked.connect(self.prevTrial)
        grid.addWidget(button, 1,0)

        button = QtGui.QPushButton('->')
        button.setToolTip("Next trial")
        button.clicked.connect(self.nextTrial)
        grid.addWidget(button, 1, 3)

        ## The slider used to navigate throughout the trials.
        self.fileslider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.fileslider.setMinimum(1)
        self.fileslider.setToolTip("File slider")

        ## The slider used to navigate through the trials.
        self.trialslider= QtGui.QSlider(QtCore.Qt.Horizontal)
        self.trialslider.setMinimum(1)
        self.trialslider.setToolTip("Trial slider")
        
        self.fileslider.sliderReleased.connect(self.fileSliderChanged)
        self.trialslider.sliderReleased.connect(self.trialSliderChanged)

        grid.addWidget(self.trialslider, 1, 1)
        grid.addWidget(self.fileslider , 2, 1)
        assert(self.custom_widget != None)
        grid.addWidget(self.custom_widget, 0, 0, 1, -1)
        
        self.setLayout(grid)
        self.show()

    ##
    # handle key presses.
    def keyPressEvent(self, event):
        ''' Capture F5 to reload with current settings. '''
        key = event.key()
        if key == QtCore.Qt.Key_F5:
            self.controller.reload()
            self.updateFromModel()
        return super(DataView, self).keyPressEvent(event)
    
    ##
    # Sets sliders the the value mentionned in the model.
    #
    # If there is only one file, the file slider will be hidden.
    # This function modifies the slider setting to match the model.
    #
    def updateSliders(self):
        nfiles = len(self.MODEL.files) 
        if nfiles > 1:
            self.fileslider.show()
            if self.fileslider.maximum() != nfiles:
                self.fileslider.setMaximum(nfiles)
            if self.fileslider.value() != self.MODEL.fileindex+1:
                self.fileslider.setValue(self.MODEL.fileindex+1)
        else:
            self.fileslider.hide()

        if self.trialslider.maximum() != len(self.MODEL.trials):
            self.trialslider.setMaximum(len(self.MODEL.trials))
        if self.trialslider.value() != self.MODEL.trialindex+1:
            self.trialslider.setValue(self.MODEL.trialindex+1)

    ##
    # Updates the trial name.
    def updateTitle(self):
        filename = os.path.split(self.MODEL.files[self.MODEL.fileindex])[1]
        trial = self.MODEL.trialindex + 1
        title = "File {0}: trial {1}".format(filename, trial)
        if not self.hasValidData():
            title += " (NO VALID DATA IN TRIAL)"
        self.setWindowTitle(title)
    
    ##
    # updates the view, to be consistent with the model
    def updateFromModel(self):
        self.updateSliders()
        self.updateTitle()
        self.custom_widget.updateFromModel()

    ##
    # Slot called when the user updates the trial slider.
    def trialSliderChanged(self):
        val = self.trialslider.value()
        self.controller.setTrialIndex(val - 1)
        self.updateFromModel()

    ##
    # Slot called when the user updates the file slider.
    def fileSliderChanged(self):
        val = self.fileslider.value()
        self.controller.setFileIndex(val - 1)
        self.updateFromModel()

    ##
    # Callback that is called when the user presses the next trial button
    def nextTrial(self):
        self.controller.nextTrial()
        self.updateFromModel()
    
    ##
    # Callback that is called when the user presses the previous trial button
    def prevTrial(self):
        self.controller.prevTrial()
        self.updateFromModel()

##
# Like DataView, but also usable to edit the experimental data.
# 
# Does almost the same as dataview, however it tries to save the data if the
# user navigates to a new experiment, or when the view is closed.
class EditDataView(DataView):
    
    ##
    # Makes the controller save the experiment
    #
    def save(self):
        ## \todo create a custom filedialog for loading and saving files.
        cur = self.MODEL.getCurrentFileName()
        Dir = os.path.dirname(cur)
        fn= QtGui.QFileDialog.getSaveFileName(caption          = "Select or enter savefile name.",
                                              directory        = Dir,
                                              filter           = "EyeData (*.csv *.asc);;all (*)",
                                              selectedFilter   = "EyeData"
                                              )
        if fn:
            self.controller.saveExperiment(fn, True)
 
    ##
    # Determine whether we must save the current experiment.
    #
    # firstly this function determines whether the experiment must be saved.
    # If it must be saved is also is going to save it. And it determines
    # whether we should advance to the next trial or allow closing
    # of the view.
    #
    # \returns True if we should advance or False if the user cancelled the
    # closing of the window or going to the next trial
    def determineSaveExperiment(self):
        if self.MODEL.isExperimentModified() or self.MODEL.isTrialModified():
            import pdb
            pdb.set_trace()
            dlg = savedialog.SaveDialog()
            ret = dlg.exec_()
            if      ret == dlg.Save:
                self.save()
            elif    ret == dlg.Cancel:
                return False
            #if ret is dlg.Discard just return True
        return True
    
    ##
    # Determines whether the experiment must be saved, and whether
    # to advance to the next trial.
    def nextTrial(self):
        if self.MODEL.getTrialIndex() == self.MODEL.getTrialMaxIndex():
            if self.determineSaveExperiment():
                super(EditDataView, self).nextTrial()
            else:
                return
        return super(EditDataView, self).nextTrial()
    
    ##
    # Determines whether the experiment must be saved, and whether
    # to return to the previous trial.
    def prevTrial(self):
        if self.MODEL.getTrialIndex() == 0:
            if self.determineSaveExperiment():
                return super(EditDataView, self).prevTrial()
            else:
                return
        return super(EditDataView, self).prevTrial()

    ##
    # Determines whether the experiment must be saved, and whether
    # to close the window.
    def closeEvent(self, event):
        if self.determineSaveExperiment():
            return super(EditDataView, self).closeEvent(event)
        else:
            event.ignore();

    ##
    # handles Keypresses
    #
    # Currently the widget accepts:
    # # Ctrl+z  Undos edit
    # # Ctrl+r  redo edit
    # # Ctrl+y  redo edit
    # # Ctrl+a  select all (visible) fixations
    # # Ctrl+s  save experiment
    def keyPressEvent(self, event):
        handled = False
        if event.modifiers() == QtCore.Qt.ControlModifier:
            handled = True
            if event.key() == QtCore.Qt.Key_Z:
                self.controller.undoEdit()
            elif event.key() == QtCore.Qt.Key_R or event.key() == QtCore.Qt.Key_Y:
                self.controller.redoEdit()
            elif event.key() == QtCore.Qt.Key_S:
                self.determineSaveExperiment()
            else:
                handled = False
        elif event.modifiers() == QtCore.Qt.NoModifier:
            handled = True
            if event.key() == QtCore.Qt.Key_F5:
                handled == True ## we just want to update from the model
            else:
                handled = False
        if handled:
            self.updateFromModel()
        else:
            super(EditDataView, self).keyPressEvent(event)

