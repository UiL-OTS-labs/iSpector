#!/usr/bin/env python

##
# \file datamodel.py This file contains the data models and controllers of iSpector.
# 
# This is the file that contains the Controllers and Models from a 
# Model View Controller design.
#
# \package gui

import copy
import utils.stack
from log.eyelog import LogEntry
from log.parseeyefile import parseEyeFile
from log.eyeexperiment import EyeExperiment 
from log.eyedata import EyeData
from log import eyelog
from os import path

##
# DataModel helps listing the files in a ordely manner.
#
# DataModel is the basic model to do something with the eyemovement
# data. The model knows which files are loaded and it knows about
# the EyeExperiment, that is all events that took place in an
# experiment.
# Since application might want to report something back to the
# mainwindow status box and, might need the global settings
# regarding fixation detection, the main window is part of the
# model, but should be considered constant.
#
class DataModel(object):
    
    ##
    # The DataModel takes a number of files. And a reference to the mainwindow.
    #
    # \param [in] files a list of files
    # \param [in] mainwindow the mainwindow of iSpector
    #
    def __init__(self, files, mainwin):
        assert(files and mainwin)
        ## all files taken in to account
        self.files      = files
        ## a reference to the main window
        self._MAINWIN   = mainwin
        ## The entire data set of one experiment
        self.experiment = None
        ## the data of one trial out of a experiment
        self.trials     = None
        ## an index to the right file to examine
        self.fileindex  = -1
        ## an index to the right trial to examine
        self.trialindex = -1
        ## the view of the model
        self._VIEW       = None

        # Sets the file and loads the file
        self.setFileIndex(0)
        # Sets the trial
        self.setTrialIndex(0)

    ##
    # This is a test to see if a model has valid data.
    #
    # The standard model doesn't require much more than
    # there are a number of files with trials to be examined.
    #
    # In a subclass one probably wants to do more advanced
    # data checking.
    def hasValidData(self):
        return len(self.files) > 0 and len(self.trials) > 0

    ##
    # Loads the eyefile with from self.files[self.fileindex]
    #
    # This function loads the file from self.files with index self.fileindex.
    # It parses the eyefile and reads all entries. And it creates an experiment
    # and all of its trials.
    def loadEyeFile(self):
        fid = self.files[self.fileindex]
        pr = parseEyeFile(fid)
        entries = pr.getEntries()
        if not entries:
            errors = pr.getErrors()
            for i in errors:
                self._MAINWIN.reportStatus(i[2], i[0] + ':' + str(i[1]))
            return False

        MODEL = self._MAINWIN.getModel()[0] # ignore the controller in the tuple

        # Optionally filter right or left gaze from the experiment
        if  (MODEL[MODEL.EXTRACT_RIGHT] and MODEL[MODEL.EXTRACT_LEFT]) or\
            (not MODEL[MODEL.EXTRACT_LEFT] and not MODEL[MODEL.EXTRACT_RIGHT]):
            pass # If both are specified or if none are specified extract both eyes
        elif MODEL[MODEL.EXTRACT_LEFT]:
            entries = LogEntry.removeRightGaze(entries)
        elif MODEL[MODEL.EXTRACT_RIGHT]:
            entries = LogEntry.removeLeftGaze(entries)
        else:
            raise RuntimeError("The control flow shouldn't get here.")

        if not entries:
            return False
        
        ##
        # an entire EyeExperiment
        self.experiment = EyeExperiment(entries)
        ##
        # an reference to the list of trials contained in self.experiment
        self.trials     = self.experiment.trials

        # The file is loaded so call onFileLoaded()
        self.onFileLoaded()

        return True
    
    ##
    # Set a new fileindex
    #
    # Set a new fileindex and load a the new eyefile.
    # This is only done when n is unequal to the current fileindex.
    #
    # \param n a valid index in the interval wich meets 0 >= n < len(self.files)
    def setFileIndex(self, n):
        assert(n >= 0 and n < len(self.files))
        if n == self.fileindex:
            return
        
        self.fileindex = n
        self.loadEyeFile()

    ##
    # Returns the current file index
    def getFileIndex(self):
        return self.fileindex

    ##
    # returns the current filename
    # \return a string or None is not applicable
    def getCurrentFileName(self):
        return self.files[self.fileindex]

    ##
    # Returns the maximum allowed file index
    def getMaxFileIndex(self):
        return len(self.files) - 1

    ##
    # Set a new trialindex
    #
    # Set a new trial to display. If the n is equal to the self.trialindex
    # this function does nothing, otherwise it sets the new trialindex
    # and call self.onNewTrial.
    #
    # \param n a valid integer which meets 0 >= n < len(self.trials)
    #
    def setTrialIndex(self, n):
        # check whether n is valid and different
        assert(n >= 0 and n < len(self.trials))
        if n == self.trialindex:
            return

        # set the new trial.
        self.trialindex = n
        self.onNewTrial()
    
    ##
    # Returns the current trial index
    def getTrialIndex(self):
        return self.trialindex

    ##
    # Return the maximum trial index
    def getTrialMaxIndex(self):
        return len(self.trials) - 1


    ##
    # onFileLoaded is called when a new file has been loaded.
    #
    # onFileLoaded does nothing in the current class, but it should be overload
    # in child classes, because they might want to update their model when a
    # new file is loaded.
    def onFileLoaded(self):
        raise NotImplementedError()

    ##
    # onNewTrial should be called when a new trial index has been selected.
    #
    # It does nothing here, but can be overloaded in a more substantial data
    # model.
    #
    def onNewTrial(self):
        pass

    ##
    # Return a reference to the main window
    #
    # This function can get in handy when a statusmessage should be posted
    # the main window.
    # it might be abused to get the parameter settings.
    def getMainWindow(self):
        return self._MAINWIN

    ##
    # Gives the trial object of the current trial
    def getCurrentTrial(self):
        return self.trials[self.trialindex]

    ##
    # sets the view
    def setView(self, view):
        self._VIEW = view

    ##
    # get the view
    def getView(self):
        return self._VIEW

    ##
    # indicates whether the user wants to show the left eye
    def showLeft(self):
        MM = self._MAINWIN.getModel()[0]
        return MM[MM.EXTRACT_LEFT] or (not MM[MM.EXTRACT_LEFT] and not MM[MM.EXTRACT_RIGHT])
    ##
    # indicates whether the user wants to show the right eye
    def showRight(self):
        MM = self._MAINWIN.getModel()[0]
        return MM[MM.EXTRACT_RIGHT] or (not MM[MM.EXTRACT_LEFT] and not MM[MM.EXTRACT_RIGHT])

    ##
    # indicates whether the user wants to show the data of the average eyesignal
    def showAvg(self):
        MM = self._MAINWIN.getModel()[0]
        ret = False
        print(self, "enable avg eye in main model")
        return ret
        return MM[MM.EXTRACT_AVG]


    

##
# The model for the data to be presented.
# 
# The model holds
# a number of filenames. It holds an index of the file and
# trial to be processed.
# Finally it contains the logdata of all trials.
class ExamineDataModel(DataModel):
    
    ## The eyedata takes a number of files. And a reference to the mainwindow.
    #
    #@param [in] files a list of files
    #@param [in] mainwindow the mainwindow of iSpector
    #
    def __init__(self, files, mainwin):
        ##
        # Contains the data to inspect/examine
        self.eyedata = None
        super(ExamineDataModel, self).__init__(files, mainwin)

    ##
    # If a new trial is selected, a new trial should be loaded.
    # 
    def onNewTrial(self):
        self._loadEyeData()

    ##
    # Does nothing, it just prevents DataModel.onFileLoaded from being called
    def onFileLoaded(self):
        pass

    ##
    # Loads an EyeData instance for one trial.
    def _loadEyeData(self):
        trial = self.trials[self.trialindex]
        # We only want to read the model thus no need to get the controller
        MM      = self._MAINWIN.getModel()[0]
        thres   = MM[MM.THRESHOLD]
        nthres  = MM[MM.NTHRESHOLD]
        smooth  = MM[MM.SMOOTH]
        win     = MM[MM.SMOOTHWIN]
        order   = MM[MM.SMOOTHORDER]

        self.eyedata = EyeData(thres, nthres, smooth, win, order)
        self.eyedata.processTrial(trial)


##
# This data model contains everything to examine a/multiple eye movement files.
# 
# This data model is more expensive than the default ExamineDataModel, however
# it is more capable to edit the data in the experiments or files.
# This way it is possible to maintain some edits and
# save those edits when necessary.
#
class EditDataModel (DataModel):
    
    ## operation succeeded
    OK          = 0
    ## file name already exists
    FN_EXISTS   = 1

    ## The eyedata takes a number of files. And a reference to the mainwindow.
    #
    # @param [in] files a list of files
    # @param [in] mainwindow the mainwindow of iSpector
    #
    def __init__(self, files, mainwin):
        super(EditDataModel, self).__init__(files, mainwin)
        ## The data of the current experiment
        self._current_experiment = None
        ## The data of the current eyetrial
        self._current_eyetrial   = None
        ## holds all modifications to the EditDataModel
        self._stack = utils.stack.Stack()
        ## holds the number of edit undo's
        self.nth_undo = 0

    ##
    # clears the current stack and sets the nth_undo back to 0
    def _clearStack(self):
        self._stack = utils.stack.Stack()
        self.nth_undo = 0

    ##
    # undo last edit
    def undoEdit(self):
        self.nth_undo += 1
        if self.nth_undo >= len(self._stack):
            self.nth_undo = len(self._stack) - 1

    ##
    # redo last edit
    def redoEdit(self):
        self.nth_undo -= 1
        if self.nth_undo < 0:
            self.nth_undo = 0

    ##
    # pushes new edit on the stack
    #
    # If a user has undone some edits the user now permanently loses those
    # changes. 
    def pushEdit(self, edit):
        if self.nth_undo != 0:
            self._stack.shrink(self.nth_undo)
            self.nth_undo = 0
        self._stack.push(edit)

    ##
    # Returns the current edit
    # otherwise it returns None
    #
    def getCurrentEdit(self):
        if len(self._stack):
            return self._stack[self.nth_undo]
        else:
            return None

    ##
    # return the currently active trial that is being editted.
    def getCurrentTrial(self):
        return self._current_eyetrial

    ##
    # Pushes the initial edit to the stack.
    # 
    # The stack should never be empty in practise the initial state
    # holds one edit that is identical to the start position
    # Once the current trial is loaded there must be one edit
    #
    # \note Must be implemented in derived class
    # \abstract
    def _pushInitialEdit(self):
        msg = "_pushInitialEdit must be implemented in derived class"
        raise NotImplementedError(msg)

    ##
    # Save the experiment
    #
    # If edits are made we save the experiment. We also
    # swap the name in the list of files with the new file name. Then
    # if someone sets the file index back to the currently
    # edited file, they will see the updated file and not the 
    # original file.
    #
    # \param fn the file name to save the experiment to
    # \param overwrite if True and the file exists, overwrite it.
    #
    # \returns EditDataModel.OK or EditDataModel.FN_EXISTS
    def saveExperiment(self, fn, overwrite=False):
        # make sure the last edits are saved to the current trial
        if self.isEditted():
            self.addTrialToCurrentExperiment()

        if path.exists(fn) and not overwrite:
            return self.FN_EXISTS

        entries = self._current_experiment.getEntries()
        eyelog.saveForFixation(entries, fn)

        # store the name of the saved experiment instead of the opened experiment.
        ## TODO examine whether it is feasible to update the main window as well.
        self.files[self.fileindex] = str(fn)

        return self.OK
        
    
    ##
    # add Edits from the current experiment to the trial inside
    # current_experiment.
    #
    # The edits are merged into the current experiment. What the current
    # edits are is specific to a Derived class, therefore the method
    # must be implemented there.
    #
    # \abstract
    def addTrialToCurrentExperiment(self):
        raise NotImplementedError(
            "addTrialToCurrentExperiment must be called from derived class only"
            )

    ##
    # Makes itself ready for a new trial
    #
    def onFileLoaded(self):
        #super(EditDataModel, self).onFileLoaded() raise NotImplementedError
        self._current_experiment = self.experiment.copy()

    ##
    # Called when a new trial must be shown
    #
    # Clears the stack. Derived class is responsible to push some new
    # information on the stack to display.
    def onNewTrial(self):
        super(EditDataModel, self).onNewTrial()
        # Clear the stack copy the current trial and push the initial edit
        self._clearStack()
        self._current_eyetrial = copy.deepcopy(
                self._current_experiment.trials[self.trialindex]
                )
        self._pushInitialEdit()

    ##
    # Determines whether the user has made modifications to the data in the experiment
    #
    # Determines when an experiment is modified by the editor. If it is modified
    # this function can be used to request the user to save the modifications.
    #
    # \returns true if there were modifications to the experiment, False otherwise.
    def isExperimentModified(self):
        if not self.experiment:
            return False
        if self._current_experiment != self.experiment or self.isEditted():
            return True
        return False
    
    ##
    # Determines whether the data of the trial is modified.
    # This can be used update the trial.
    #
    # \returns True if there were modifications to the trial, False otherwise.
    def isTrialModified(self):
#        if not self.trialindex:
#            return False
#        try:
#            # TODO abbrieviate to return "self.getCurrentTrial() != self.trials[self.trialindex]"
#            print "same trial data= ", self._current_eyetrial == self.trials[self.trialindex]
#            if self._current_eyetrial != self.trials[self.trialindex]:
#                return True
#            else:
#                return False
#        except AttributeError as error:
#            # if we are missing some atribute it isn't initialized yet
#            # hence not modified
#            return False
        return self.isEditted()

    ##
    # Load a file with index n in self.files
    #
    # Before loading the new experiment we check if the current experiment
    # must be saved, if it must be saved. We query the user to save the
    # experiment if the user wants to save it, we save it.
    #
    # \param n a valid positive index < len(self.files)
    def setFileIndex(self, n):
        if n == self.fileindex:
            return

        super(EditDataModel, self).setFileIndex(n)

    ##
    # Set a new trialindex
    #
    # Merges the current edits to the current experiment and load
    # prepare for the new trial.
    #
    # \param n a valid integer which meets 0 >= n < len(self.trials)
    #
    def setTrialIndex(self, n):
        # check whether n is valid and different
        #print self, "setTrialIndex", n, self.trialindex, self.isTrialModified()
        if n == self.trialindex:
            return

        if self.isTrialModified():
            self.addTrialToCurrentExperiment()
        super(EditDataModel, self).setTrialIndex(n)
    
    ##
    # An edit model doesn't need an EyeData instance, so it isn't called
    # \TODO examine whether this function should only be called in a
    # ExamineDataModel.
    #
    def _loadEyeData(self):
        pass #raise NotImplementedError()

    ##
    # Determines whether edits have been made.
    #
    # It might be quite painfull to detect whether there are modifications
    # to the eyedata. Therefore if the user does something, the new
    # eyedata is push on the stack. Therefore if the the length of stack > 1
    # we assume there has been changes. This number must be corrected
    # with the number of undos.
    #
    # \returns True if the user made edits, False otherwise.
    def isEditted(self):
        try:
            if len(self._stack) - self.nth_undo > 1:
                return True
            return False
        except (AttributeError):
            # Attribute error is raised if in the contructors
            # the stack doesn't exist yet. But if it isn't
            # created yet is sure doesn't contain edits.
            return False


##
# A controller that allows to examine data in the files.
#
# This controller pairs with the ExamineDataModel it is a
# controller that lets the user move through a number of files
# and the trials within an experiment.
# This controller is not suited to edit data inside an experiment.
#
class ExamineDataController(object):
    
    ##
    # @param model an instance of ExamineDataModel
    #
    def __init__(self, model):
        ## The model that belongs to that is controlled by
        # this instance.
        self.model = model
        if not self.model.loadEyeFile():
            return
        self.setTrialIndex(0)
    
    ##
    # reloads the model with the current setting from the main window.
    def reload(self):
        self.model._loadEyeData()

    ##
    # Set the index of the file to display
    # @param n the new integer index
    #
    def setFileIndex(self, n):
        if n == self.model.fileindex:
            return
        if n < 0:
            n = 0
        if n >= len(self.model.files):
            n = len(self.model.files) -1
        self.model.setFileIndex(n)

    ##
    # Set the index of the trial to display
    #
    # Set the index within the model to a new value.
    # This should be the only function that makes
    # the data model load the eyedata, since this is
    # probably the most expensive function.
    def setTrialIndex(self, n):
        self.model.trialindex = n
        if self.model.trialindex < 0:
            self.model.trialindex = 0
        elif self.model.trialindex >= len(self.model.trials):
            self.model.trialindex = len(self.model.trials) - 1
        self.model._loadEyeData()

    ##
    # advance to the next trial(possibly of a new file)
    def nextTrial(self):
        if len(self.model.trials) <= self.model.trialindex + 1:
            self.setFileIndex(self.model.fileindex + 1)
            self.setTrialIndex(0)
            return
        self.setTrialIndex(self.model.trialindex + 1)
    
    ##
    # Present previous trial even if in the previous file.
    def prevTrial(self):
        if self.model.trialindex - 1 < 0:
            self.setFileIndex(self.model.fileindex - 1)
            self.setTrialIndex(len(self.model.trials) - 1)
            return
        self.setTrialIndex(self.model.trialindex - 1)


##
# A controller that allows to edit data in the files.
#
# This controller pairs with the EditDataModel it is a
# controller that lets the user move through a number of files
# and the trials within an experiment.
# This controller is suited to edit data inside an experiment.
#
# At some point during the editting the controller allows for
# user interaction. The user can choose whether to save or
# discard the edits.
#
class EditDataController (ExamineDataController):
    
    ##
    # @param model an instance of ExamineDataModel
    # \todo check whether the parent __init__ can't solve all of this.
    def __init__(self, model):
        super(EditDataController, self).__init__(model)

    ##
    # Save the experiment.
    #
    # \param fn         string with the filename for the new experiment.
    # \param overwrite  boolean specify whether the file should be overwritten
    # 
    # \returns gui.EditDataModel.OK if written or gui.EditDataModel.FN_EXISTS
    #          if overwrite is false and the file exists.
    def saveExperiment(self, fn, overwrite=False):
        return self.model.saveExperiment(fn, overwrite)
    
    ##
    # Reloads the model with the current setting from the main window.
    #
    # calls discardTrialModifications to examine whether the current
    # edits can be discarded.
    def reload(self):
        if self.model.isTrialModified():
            if not self.discardTrialModifications():
                return
        super(EditDataController, self).reload()

    ##
    # Set the index of the file to display and saves the current experiment
    #
    # This sets the new experiment to edit. If there were modifications
    # saveCurrentExperiment will be called to optionally save them.
    #
    # @param n the new integer index
    def setFileIndex(self, n):
        if self.model.fileindex == n:
            return
        super(EditDataController, self).setFileIndex(n)

    ##
    # Set the index of the trial to display
    #
    # If the current trial has been modified
    # merge the changes in the trial
    def setTrialIndex(self, n):
        if n == self.model.trialindex:
            return

        ## TODO examine why self.modle.setTrialIndex has to be called directly
        #       instead via the parent.
        self.model.setTrialIndex(n)

        #super(EditDataController, self).setTrialIndex(n)

    ##
    # undos last edit if possible
    def undoEdit(self):
        self.model.undoEdit()
    
    ##
    # redo last edit if possible
    def redoEdit(self):
        self.model.redoEdit()
