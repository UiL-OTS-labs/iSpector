#!/usr/bin/env python

#from log import *
from log.eyedata import *
from log.eyeexperiment import *
from log.parseeyefile import *
from PyQt4 import QtGui
from PyQt4 import QtCore

import inspecteyedataview
from gui import datamodel
import statusmessage as sm
import sys
import os
import os.path as p
import ievent
import statusbox
import utils.configfile
import iSpectorVersion
import fixationeditor


LOGO = "iSpectorLogo.svg"


class NoSuchString(Exception):
    def __init__(self,message):
        super(NoSuchString, self).__init__(message)

def comboSelectString(combo, string):
    """
    Selects the string if available does noting when the string is allready
    selected
    """
    if combo.currentText() == string:
        return
    index = combo.findText(string)
    if index < 0:
        raise NoSuchString("The string \"" + string + "\" is not available")
    else:
        combo.setCurrentIndex(index)

class Controller :
    """
    The controller keeps track if the user enters valid input inside the gui.
    if the input is valdid the controller updates the model.
    """
    
    def __init__(self, model, view):
        """
        @param Model the model that contains all parameters for succesfull parsing
        the input files and the input files themselves.
        """
        assert (model and view)
        self.model  = model
        self.view   = view
        self._initModel()

    def _initModel(self):
        """ Fixes model initially """
        self.model[self.model.STATUS] = "ready"
        
        # Only select real files and create a absolute path
        self.model.set_files(
            [p.abspath(i) for i in self.model.files() if p.isfile(i) ]
        )
        self.model.set_files(sorted(set(self.model.files())))
        
        # create selected file in the model namespace
        if self.model.files():
            #set the first file as selected
            self.model.selected.append(self.model.files()[0])

        if self.model.output_dir():
            self.updateDirectory(self.model.output_dir())

        if self.model.stimulus_dir():
            self.updateStimDir(self.model.stimulus_dir())

    def updateAction(self, string):
        self.model[self.model.ACTION] = string

    def updateStatus(self, string):
        s = str(string)
        self.model[self.model.STATUS] = s

    def updateEye(self, string):
        if string == "left":
            self.model[self.model.EXTRACT_LEFT]=True
            self.model[self.model.EXTRACT_RIGHT]=False
        elif string == "right":
            self.model[self.model.EXTRACT_LEFT]=False
            self.model[self.model.EXTRACT_RIGHT]=True
        elif string == "both":
            #if both are false default is to select both
            self.model[self.model.EXTRACT_LEFT]=False
            self.model[self.model.EXTRACT_RIGHT]=False
        else:
            raise RuntimeError("Invalid string in updateEye")

    def updateSmooth(self, state):
        if state == QtCore.Qt.Checked:
            if self.model[self.model.SMOOTH]:
                # everything is already alright
                return
        elif state == QtCore.Qt.Unchecked:
            if not self.model[self.model.SMOOTH]:
                #everything is ok
                return
        else:
            raise ValueError("state must be either QtCore.Qt.Checked or Unchecked")
        
        self.model[self.model.SMOOTH] = not self.model[self.model.SMOOTH]

    def updateSmoothWindowSize(self, string):
        value = int(string)
        if value % 2 == 0 or value < 3:
            raise ValueError("Value must be odd and larger then 2")
        self.model[self.model.SMOOTHWIN] = value

    def updateSmoothOrder(self, string):
        value = int(string)
        if value < 1:
            raise ValueError("Smoothorder isn't Smootorder > 0")
        self.model[self.model.SMOOTHORDER] = value

    def updateThreshold(self, string):
        if string == "mean":
            self.model[self.model.THRESHOLD] = "mean"
        elif string == "median":
            self.model[self.model.THRESHOLD] = "median"
        else:
            raise ValueError(("The method for determining the threshold must be"
                              "either mean or median")
                              )
    
    def updateNThreshold(self, real):
        """
        set the number of times the mean or median must be taken to get
        the threshold.
        @param real number larger than 0
        """
        value = float(real)
        if value <= 0.0:
            return
        self.model[self.model.NTHRESHOLD] = value

    def updateFiles(self, filenamelist):
        """ set filenamelist as the new selected files. """
        filenamelist = [str(i) for i in filenamelist]
        for i in filenamelist:
            #remove possible dupplicates
            if not (i in self.model.files()):
                self.model.files().append(i)
        self.model.files().sort()

    def updateDefaultOpenDir(self, d):
        """
        Store the default open directory
        """
        if p.isdir(d):
            dirs = self.model.set_file_dir(d)

    def updateDirectory(self, dirname):
        """ updates the output directory to be dirname """
        dirname = str(dirname)
        if p.isdir(dirname):
            self.model.set_output_dir(p.abspath(dirname))
        else:
            self.model.set_output_dir(p.abspath("."))
    
    def updateStimDir(self, dirname):
        """ updates the stimulus directory to be dirname """
        dirname = str(dirname)
        if p.isdir(dirname):
            self.model.set_stimulus_dir(p.abspath(dirname))
        else:
            self.model.set_stimulus_dir(p.abspath("."))

    def updateSelected(self, flist):
        """ Sets the new selected items in the file list. """
        flist = sorted([str(i) for i in flist])
        if flist != self.model.selected:
            self.model.selected = flist

    def removeSelected(self, flist):
        """ Remove items selected for an action"""
        flist = [str(i) for i in flist]
        removeset   = set(flist)
        oldset      = set(self.model.files())
        newset      = oldset - removeset
        self.model.selected = []
        self.model.set_files(list(sorted(newset)))


class DirGroup (QtGui.QGroupBox):
    """
    The dirgroup handles all directories that are useful for
    The program.
    """
    def __init__(self, controller, model, mainwindow):
        super(DirGroup, self).__init__("Directories")
        self.controller = controller
        self.MODEL      = model
        self.grid       = QtGui.QGridLayout()
        self.mainwindow = mainwindow
        self._init()

    def _init(self):
        verticalbox = QtGui.QVBoxLayout()
        self.setLayout(verticalbox)
        
        # Adding widgets to select the output directory
        self.outdirlabel    = QtGui.QLabel("Output directory:")
        self.outdiropenicon = QtGui.QIcon.fromTheme("folder")
        self.outdirbutton   = QtGui.QPushButton(self.outdiropenicon, "open")
        self.outdirbox      = QtGui.QHBoxLayout()
        
        # Setting tooltips and adding the directory widgets to the directory HBox
        self.outdirbutton.setToolTip("Select directory to write the output to.")
        self.outdirbox.addWidget(self.outdirlabel, 1, alignment=QtCore.Qt.AlignLeft)
        self.outdirbox.addWidget(self.outdirbutton)
        
        # Adding widgets to select the output directory
        self.stimdirlabel   = QtGui.QLabel("Stimulus directory:")
        self.stimdiropenicon= QtGui.QIcon.fromTheme("folder")
        self.stimdirbutton  = QtGui.QPushButton(self.stimdiropenicon, "open")
        self.stimdirbox     = QtGui.QHBoxLayout()

        # Setting tooltips and adding the directory widgets to the directory HBox
        self.stimdirbutton.setToolTip("Select directory to search for stimuli.")
        self.stimdirbox.addWidget(self.stimdirlabel, 1, alignment=QtCore.Qt.AlignLeft)
        self.stimdirbox.addWidget(self.stimdirbutton)

        # Connect signals
        self.outdirbutton.clicked.connect(self._openOutDir)
        self.stimdirbutton.clicked.connect(self._openStimDir)

        verticalbox.addLayout(self.outdirbox)
        verticalbox.addLayout(self.stimdirbox)
        self.setLayout(verticalbox)
    
    def _setOutDirlabel(self, dirname):
        name = "Output directory:\n \"{0:s}\"".format(dirname)
        self.outdirlabel.setText(name)
    
    def _setStimDirlabel(self, dirname):
        name = "Stimulus directory:\n \"{0:s}\"".format(dirname)
        self.stimdirlabel.setText(name)

    def updateFromModel(self):
        """ examines the model. """
        self._setOutDirlabel(self.MODEL.output_dir())
        self._setStimDirlabel(self.MODEL.stimulus_dir())
    
    def _openOutDir(self):
        """ Shows the file dialog to choose a new dir. """
        d   = self.MODEL.output_dir()
        folder = QtGui.QFileDialog.getExistingDirectory(
                                               caption          = "Select output directory",
                                               directory        = d
                                               )
        if folder:
            self.controller.updateDirectory(folder)
        self.updateFromModel()
    
    def _openStimDir(self):
        """ Shows the file dialog to choose a new dir. """
        d   = self.MODEL.stimulus_dir()
        folder = QtGui.QFileDialog.getExistingDirectory(
                                               caption          = "Select stimulus directory",
                                               directory        = d
                                               )
        if folder:
            self.controller.updateStimDir(folder)
        self.updateFromModel()


class OptionGroup(QtGui.QGroupBox):
    """
    Option group contains mainly the parameters to control
    the detection of fixations and saccades. It
    also sets the main action of iSpector to either
    inspect the data or to extract it forFixation.
    """
    
    actiontip       =("Select <b>inspect</b> to look at the file, and\n"
                      "<b>extract</b> to create output for fixation.")
    smoothtip       =("Check to smooth the data with a Savitsky-Golay filter\n"
                      "Note: use the same smoothing values over an entire experiment\n"
                      "because smoothing values has an influence on the duration\n"
                      "of saccades and fixations.")
    eyetip          = "Select the eye to inspect/extract."
    smoothwintip    =("Select a value for the window size of the smoothing filter\n"
                      "a bigger value means stronger smoothing.\n"
                      )
    smoothordertip  =("Select the polynomial order for the smoothing function\n"
                      "using order=1 means you are using a moving average.")
    thresholdtip    =("Use mean or median to set the threshold for determining the\n"
                      "difference between fixations and saccades.")
    nthresholdtip   =("Enter a real number. This number is used to multiply with the\n"
                      "threshold to find the final value over the data. So the\n"
                      "final threshold = nthreshold * <mean|median>.")
    
    def __init__(self, controller, model, mainwindow):
        super(OptionGroup, self).__init__("Options")
        self.controller = controller
        self.MODEL      = model
        self.grid       = QtGui.QGridLayout()
        self.mainwindow = mainwindow
        self._init()

    def _handle(self, arg1=None):
        """ calls the right event handler and updates the view """
        self.handlers[self.sender()](arg1)
        self.mainwindow.updateFromModel()

    def handleAction(self, index):
        string = self.actioncombo.itemText(index)
        self.controller.updateAction(string)

    def handleEye(self, index):
        string = self.eyecombo.itemText(index)
        self.controller.updateEye(string)

    def handleSmooth(self, value):
        self.controller.updateSmooth(value)

    def handleSmoothOrder(self, index):
        string = self.ordercombo.itemText(index)
        self.controller.updateSmoothOrder(string)

    def handleSmoothWindow(self, index):
        string = self.windowcombo.itemText(index)
        self.controller.updateSmoothWindowSize(string)

    def handleThreshold(self, index):
        string = self.thresholdcombo.itemText(index)
        self.controller.updateThreshold(string)

    def handleNThreshold(self, event):
        string = self.nthresholdentry.text()
        self.controller.updateNThreshold(string)

    def _init(self):
        """ place all Qt widgets on the in a grid
            and put the grid inside the groupwidget
        """
        self.setFlat(False)
        self.setLayout(self.grid)
        self._addLabel(u"Action:",      0, 0)
        self._addLabel(u"Inspect/Extract eye:", 1, 0)
        self._addLabel(u"Smooth:",      2, 0)
        self._addLabel(u"Smoothwindow:",3, 0)
        self._addLabel(u"Smoothorder:", 4, 0)
        self._addLabel(u"Threshold:",   5, 0)
        self._addLabel(u"NThreshold:",  6, 0)
        
        # A combobox that sets the main action of the program.
        combo = QtGui.QComboBox()
        combo.setToolTip(self.actiontip)
        combo.addItems(MainGuiModel.VALID_ACTIONS)
        combo.activated.connect(self._handle)
        self.grid.addWidget(combo, 0, 1)
        self.actioncombo = combo
        
        # Select the eye(s) to inspect or extract.
        combo = QtGui.QComboBox()
        combo.setToolTip(self.eyetip)
        combo.addItems(["left", "right", "both"])
        combo.activated.connect(self._handle)
        self.grid.addWidget(combo, 1, 1)
        self.eyecombo = combo

        # Allow the user to select smoothing via this checkbox.
        checkbox = QtGui.QCheckBox()
        checkbox.setToolTip(self.smoothtip)
        checkbox.stateChanged.connect(self._handle)
        self.grid.addWidget(checkbox, 2, 1)
        self.smoothcheckbox = checkbox

        # Allow the user to select a smoothing window size
        # all windowsizes are valid.
        combo = QtGui.QComboBox()
        combo.setToolTip(self.smoothwintip)
        combo.addItems([str(i) for i in range(3,21, 2)])
        combo.activated.connect(self._handle)
        self.grid.addWidget(combo, 3, 1)
        self.windowcombo = combo

        # Let the user select a valid smooting order
        # for the Savitsky-golay filter.
        combo = QtGui.QComboBox()
        combo.setToolTip(self.smoothordertip)
        combo.addItems(["1", "2", "3", "4", "5"])
        combo.activated.connect(self._handle)
        self.grid.addWidget(combo, 4, 1)
        self.ordercombo = combo

        # Let the user select the method to set the base threshold.
        combo = QtGui.QComboBox()
        combo.setToolTip(self.thresholdtip)
        combo.addItems(["median", "mean"])
        combo.activated.connect(self._handle)
        self.grid.addWidget(combo, 5, 1)
        self.thresholdcombo = combo

        # allow the user to express a factor to select the final threshold
        # So the final threshold = base threshold * the value they enter here.
        entry = QtGui.QLineEdit()
        validator = QtGui.QDoubleValidator()
        validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        validator.setRange(0, 99, 4)
        entry.setValidator(validator)
        entry.setText(str(self.MODEL[self.MODEL.NTHRESHOLD]))
        entry.setToolTip(self.nthresholdtip)
        entry.editingFinished.connect(self._handle)
        self.grid.addWidget(entry, 6, 1)
        self.nthresholdentry = entry

        # when a event happens this class maps the sender(the key)
        # to the handler(value) of the next dict. the handler
        # will handle the event.
        self.handlers = {
            self.actioncombo        : self.handleAction,
            self.eyecombo           : self.handleEye,
            self.smoothcheckbox     : self.handleSmooth,
            self.windowcombo        : self.handleSmoothWindow,
            self.ordercombo         : self.handleSmoothOrder,
            self.thresholdcombo     : self.handleThreshold,
            self.nthresholdentry    : self.handleNThreshold
        }
    
    def _addLabel(self, string, row , column, rowspan=1, heightspan=1):
        """ utility to add labels to the layout """
        label = QtGui.QLabel(string)
        self.grid.addWidget(label, row, column, rowspan, heightspan)
        label.show()

    def updateFromModel(self):
        """ Sets the options combo to the values in the model. """
        comboSelectString(self.actioncombo, self.MODEL[self.MODEL.ACTION])

        if ((self.MODEL[self.MODEL.EXTRACT_LEFT] and self.MODEL[self.MODEL.EXTRACT_RIGHT] ) or
            (not self.MODEL[self.MODEL.EXTRACT_LEFT] and not self.MODEL[self.MODEL.EXTRACT_RIGHT])):
            comboSelectString(self.eyecombo, "both")
        elif self.MODEL[self.MODEL.EXTRACT_LEFT]:
            comboSelectString(self.eyecombo, "left")
        else:
            comboSelectString(self.eyecombo, "right")

        if self.MODEL[self.MODEL.SMOOTH]:
            self.smoothcheckbox.setCheckState(QtCore.Qt.Checked)
            self.windowcombo.setEnabled(True)
            self.ordercombo.setEnabled(True)
            try:
                comboSelectString(self.windowcombo, str(self.MODEL[self.MODEL.SMOOTHWIN]))
            except NoSuchString as e:
                sys.stderr.write(e.message + "\n")
            try:
                comboSelectString(self.ordercombo, str(self.MODEL[self.MODEL.SMOOTHORDER]))
            except NoSuchString as e:
                sys.stderr.write(e.message + "\n")
        else:
            self.smoothcheckbox.setCheckState(QtCore.Qt.Unchecked)
            self.windowcombo.setEnabled(False)
            self.ordercombo.setEnabled(False)

        comboSelectString(self.thresholdcombo, self.MODEL[self.MODEL.THRESHOLD])

        self.nthresholdentry.setText(str(self.MODEL[self.MODEL.NTHRESHOLD]))


class FileEntry(QtGui.QListWidgetItem):
    """ FileEntry can be cast to string. It displays the
        filename, but keeps the directory in mind.
    """
    
    def __init__(self, directory, fname, parent):
        super(FileEntry, self).__init__(fname, parent)
        self.directory = directory
        self.fname = fname
        self.setToolTip(str(self))

    def __str__(self):
        """ Create absolute pathname. """
        return p.join(self.directory, self.fname)

class FileEntryList(QtGui.QListWidget) :
    """
    Handles delete keypress to remove one entry from
    the model and view.
    """
    def __init__(self, FileView,  parent=None):
        super(FileEntryList, self).__init__(parent)
        self.view = FileView 

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Delete:
            self.view.removeSelected()

class InputOutput(QtGui.QVBoxLayout) :
    """
    InputOutput helps to display the files used
    as input for the fixation dectection algorithms
    either to display them or to extract data
    for Fixation. It also allows to set the output
    directory.
    """

    FILTERS     = u"EyeData (*.csv *.asc);;all (*)"
    EYE_FILT    = u"EyeData"
    
    def __init__(self, controller, model):
        """ initializes model, controller and finally the gui elements"""
        super(InputOutput, self).__init__()
        self.MODEL      = model
        self.controller = controller
        self.files = [] # the input files
        self._init()

    def _init(self):
        """ Initializes the gui elements """
        label = QtGui.QLabel("Input files:")
        self.addWidget(label)

        self.fileviewwidget = FileEntryList(self)#QtGui.QListWidget()
        self.fileviewwidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.fileviewwidget.itemSelectionChanged.connect(self.onSelection)
        self.addWidget(self.fileviewwidget)
        
    def onSelection(self):
        """ Called when selection changes. """
        items = self.fileviewwidget.selectedItems()
        self.controller.updateSelected(items)
        #don't update, causes infinite recursion

    def _openFiles(self):
        """ This opens files, and updates the data model. """
        d = self.MODEL.file_dir()
        l = QtGui.QFileDialog.getOpenFileNames(caption          = "Select input file(s)",
                                               directory        = d,
                                               filter           = self.FILTERS,
                                               selectedFilter   = self.EYE_FILT
                                               )
        if l:
            self.controller.updateFiles(l)
            path = str(l[0])
            self.controller.updateDefaultOpenDir(p.dirname(path))
            self.updateFromModel()

    def removeSelected(self):
        """ delete selected item's """
        l = self.fileviewwidget.selectedItems()
        self.controller.removeSelected(l)
        self.updateFromModel()

    def updateFromModel(self):
        """ Add filenames to view """
        modelset = set (self.MODEL.files())
        currentset = set([])
        selected = self.MODEL.selected
        itemlist = self.fileviewwidget.findItems("*", QtCore.Qt.MatchWildcard)
        for i in itemlist:
            currentset.add(str(i))

        currentset = currentset & modelset
        self.fileviewwidget.clear()
        for i in self.MODEL.files():
            directory, filename = p.split(i)
            item = FileEntry(directory, filename, self.fileviewwidget)
            if i in selected:
                item.setSelected(True)
            else:
                item.setSelected(False)
        
##
# The main window of iSpector
#
# This is the main window. It is essentially no longer a wrapper around the
# commandline arguments of examine_csv.
#
# \note ispector actually started as a terminal program instead of a gui
#       some things just keep expanding :D!!
class ISpectorGui(QtGui.QMainWindow):

    ## window title, can still be improved
    _WINDOW_TITLE = iSpectorVersion.getVersion() +\
                    " (if it starts with eye it \"must\" be good)"
    
    ##
    # Construct the main window.
    def __init__(self, model):
        """ Inits the main window """
        super(ISpectorGui, self).__init__()
        
        ## the controller from a MVC gui implementation
        self.controller = Controller(model, self)
        ## the model from a MVC gui implementation
        self.MODEL      = model

        # init Qt related stuff
        self._init()

    ##
    # Add all gui stuff to the main window.
    def _init(self):
        # Set main window appearance.
        self.setWindowTitle(self._WINDOW_TITLE)
        self.setWindowIcon(QtGui.QIcon(LOGO))

        # Adding main widget to the window
        centralwidget = QtGui.QWidget(self)
        self.setCentralWidget(centralwidget)
        ## a grid to layout all other widgets.
        self.grid = QtGui.QGridLayout()
        self.grid.setColumnStretch(1, 1)
        self.grid.setColumnStretch(0,10)
        centralwidget.setLayout(self.grid)

        # Make the options
        ## a OptionGroup to configure "global" parameters.
        self.options = OptionGroup(self.controller, self.MODEL, self)
        self.options.setFlat(False)
        self.grid.addWidget(self.options, 0, 1)

        # Create the directory widget
        self.dirs    = DirGroup(self.controller, self.MODEL, self)
        self.dirs.setFlat(False)
        self.grid.addWidget(self.dirs, 1, 1)

        ## The file selector
        self.files = InputOutput(self.controller, self.MODEL)
        self.grid.addLayout(self.files, 0, 0, 2,1, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        ## The action button to start the iSpector action.
        self.actionbutton = QtGui.QPushButton("")
        self.actionbutton.clicked.connect(self.doAction)
        self.grid.addWidget(self.actionbutton, 3, 1, alignment=QtCore.Qt.AlignRight)

        ## The box wherein status messages are displayed.
        self.statusbox = statusbox.StatusBox()
        templayout = QtGui.QVBoxLayout();
        templabel = QtGui.QLabel("Status messages: ")
        templayout.addWidget(templabel)
        templayout.addWidget(self.statusbox)
        self.grid.addLayout(templayout, 2, 0, 1, 2)

        # create exit handeling and keyboard short cuts.
        icon        = QtGui.QIcon.fromTheme("window-close")
        exitAction  = QtGui.QAction(icon, '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)

        icon        = QtGui.QIcon.fromTheme("document-open")
        openAction  = QtGui.QAction(icon, '&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open file(s)')
        openAction.triggered.connect(self.files._openFiles)
        
        # add menubar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        fileMenu.addAction(openAction)
        
        # Update the entire window before showing it.
        self.updateFromModel()

        self.show()
    
    ##
    # Catch events related check to see whether it is a status event.
    #
    # The event event is overwritten to capture custom user events.
    # for example if a user reports a status
    #
    def event(self, e):
        if e.type() == ievent.StatusEvent.my_user_event_type:
            status = e.get_status()
            self.statusbox.addMessage(status)
            return True
        return super(ISpectorGui, self).event(e)

    ##
    # returns a tuple of data model and the controller
    def getModel(self):
        return self.MODEL, self.controller

    ##
    # Show a status message in iSpector main gui.
    #
    # This function shows a status message in the iSpectorgui.
    # since it posts an event it should be threadsafe.
    #
    # \param status one of StatusMessage.ok, error or warning.
    # \param message a string with information to display.
    def reportStatus(self, status, message):
        status =  sm.StatusMessage(status, message)
        event = ievent.StatusEvent(status)
        QtGui.QApplication.postEvent(self, event)

    ##
    # Read the model and update the view.
    def updateFromModel(self):
        self.statusBar().showMessage(self.MODEL[self.MODEL.STATUS])
        self.options.updateFromModel()
        self.files.updateFromModel()
        self.dirs.updateFromModel()

        actiontxt = self.MODEL[self.MODEL.ACTION]
        self.actionbutton.setText(actiontxt)

    ##
    # Examines all selected files.
    def examine(self, filelist):
        filelist = []
        if len(self.MODEL.selected) > 0:
            filelist = self.MODEL.selected
        else:
            filelist = self.MODEL.files()
        
        model = datamodel.ExamineDataModel(filelist, self)
        controller = datamodel.ExamineDataController(model)
        examinewidget = inspecteyedataview.InspectEyeDataView(model,
                                                              controller,
                                                              self
                                                              )
        if examinewidget.hasValidData():
            examinewidget.show()
        else:
            self.reportStatus(statusmessage.StatusMessage.error,
                              "Unable to load valid data for inspection.")

    def editFixations(self, filelist):
        filelist = []
        if len(self.MODEL.selected) > 0:
            filelist = self.MODEL.selected
        else:
            filelist = self.MODEL.files()

        model           = fixationeditor.FixationEditModel(filelist,
                                                           self,
                                                           fixationeditor.SHOW_ALL
                                                           )
        controller      = fixationeditor.FixationEditController(model)
        fix_edit_widget = fixationeditor.FixationEditView(model, controller, self)
        if fix_edit_widget.hasValidData():
            fix_edit_widget.show()
        else:
            self.reportStatus(statusmessage.StatusMessage.error,
                              "Unable to load valid data for inspection.")
        

    def _createOutputFilename(self, experiment, fname, outdir):
        """ Create a suitable output absolute pathname
            based on the input of the experiment
            or the output.
        """
        # create output filename
        expname  = experiment.getFixationName() # take a Fixation compatible output name
        tempdir, shortfname = p.split(fname)
        odir = ""
        if outdir:
            #use specified output dir
            odir = outdir
        else:
            #use origin filedir (put in- and output alongside eachother)
            odir = tempdir
        #absolute path to new filename
        absoutput = p.join(odir, expname)
        
        # Warn user if file allready exists.
        if p.exists(absoutput):
            msg = ("The file \"" + absoutput  + "\"already exits.\n"
                   "Do you want to overwrite it?")
            dlg = QtGui.QMessageBox(QtGui.QMessageBox.Warning,
                                    "File exits",
                                    msg,
                                    QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
            if dlg.exec_() == QtGui.QMessageBox.Cancel:
                return None
        return absoutput

    def extractForFixation(self, filelist, outdir=""):
        for fname in filelist:
            #inform user
            msg = "processing file: \"" + fname + "\""
            self.reportStatus(sm.StatusMessage.ok, msg)
            self.statusBar().showMessage(msg)

            pr = parseEyeFile(fname)

            entries = pr.getEntries()
            if not entries:
                # add error info to gui 
                dlg = QtGui.QMessageBox(QtGui.QMessageBox.Critical,
                                        "Parse Error",
                                        "Unable to parse \"" + fname + "\"",
                                        QtGui.QMessageBox.Ok)
                dlg.exec_()
                continue

            entries = LogEntry.removeEyeEvents(entries)

            # Optionally filter right or left gaze from the experiment
            if      (self.MODEL[self.MODEL.EXTRACT_RIGHT] and self.MODEL[self.MODEL.EXTRACT_LEFT]) or\
                    (not self.MODEL[self.MODEL.EXTRACT_LEFT] and not self.MODEL[self.MODEL.EXTRACT_RIGHT]):
                pass # If both are specified or if none are specified extract both eyes
            elif self.MODEL[self.MODEL.EXTRACT_LEFT]:
                entries = LogEntry.removeRightGaze(entries)
            elif self.MODEL[self.MODEL.EXTRACT_RIGHT]:
                entries = LogEntry.removeLeftGaze(entries)
            else:
                raise RuntimeError("The control flow shouldn't get here.")

            experiment  = EyeExperiment(entries)
            assert(experiment)

            # Obtain filename
            absoutput = self._createOutputFilename(experiment, fname, outdir)
            if not absoutput:
                continue

            # Determine our own fixations and saccades.
            for t in experiment.trials:
                if t.containsGazeData() == True:
                    thres = self.MODEL[self.MODEL.THRESHOLD]
                    nthres= self.MODEL[self.MODEL.NTHRESHOLD]
                    smooth= self.MODEL[self.MODEL.SMOOTH]
                    winsz = self.MODEL[self.MODEL.SMOOTHWIN]
                    order = self.MODEL[self.MODEL.SMOOTHORDER]
                    eyedata = EyeData(
                            thres,
                            nthres,
                            smooth,
                            winsz,
                            order
                            )
                    eyedata.processTrial(t, True)
                    lfixes, rfixes = eyedata.getFixations()
                    rsacs , lsacs  = eyedata.getSaccades()
                    entries.extend(lfixes)
                    entries.extend(rfixes)
                    entries.extend(lsacs)
                    entries.extend(rsacs)
            
            # finally save the output.
            saveForFixation(entries, absoutput)
        self.controller.updateStatus("Finished")
        self.updateFromModel()

    def doAction(self):
        """
        Runs the action either to inspect or extract the selected items
        """
        files = self.MODEL.selected
        if not files:
            # if no files are selected ask whether all files in the 
            # listview should be processed.
            self.reportStatus(sm.StatusMessage.warning,
                    "No files selected running action on all files")
            
            files = self.MODEL.files()
        if not files:
            return

        if self.MODEL[self.MODEL.ACTION] == self.MODEL.EXTRACT:
            d = self.MODEL.output_dir()
            self.extractForFixation(files, d)
        elif self.MODEL[self.MODEL.ACTION] == self.MODEL.INSPECT:
            self.examine(files)
        elif self.MODEL[self.MODEL.ACTION] == self.MODEL.EDIT_FIXATIONS:
            self.editFixations(files)
        else:
            raise RuntimeError("Invalid key in self.MODEL[self.MODEL.ACTION]")

    ##
    # Save config file and exit
    def closeEvent(self, event):
        self.MODEL.configfile.write()
        super(ISpectorGui, self).closeEvent(event)



class MainGuiModel(dict):
    """
    The model of the parameters of iSpector
    """

    SMOOTH          = "smooth"          ##<bool
    SMOOTHWIN       = "smoothwin"       ##<int
    SMOOTHORDER     = "smoothorder"     ##<int
    THRESHOLD       = "threshold"       ##<string
    NTHRESHOLD      = "nthreshold"      ##<float
    DRAWSACCADES    = "drawsaccades"    ##<bool
    COMPARE         = "compare"         ##<bool
    ACTION          = "action"          ##<string
    EXTRACT_LEFT    = "extract-left"    ##<bool
    EXTRACT_RIGHT   = "extract-right"   ##<bool
    #DIRS            = "dirs"            ##<dict
    #FILES           = "files"           ##<list[string]
    #SELECTED        = "selected"        ##<list[string]
    STATUS          = "status"          ##<string

    # strings releated to a certain action

    ## string used for inspecting
    INSPECT         = "inspect"
    ## string used for extracting
    EXTRACT         = "extract"
    ## string used for edit fixation action 
    EDIT_FIXATIONS  = "edit fixations"
    ## a list of strings with valid actions that iSpector can do.
    VALID_ACTIONS   = [ INSPECT,
                        EXTRACT,
                        EDIT_FIXATIONS
                        ]

    def __init__ (self, cmdargs):
        """
        First we set the values from the configuration file,
        then we set/overwrite from         
        """

        ##
        # Configurations that are stored between runs
        self.configfile = utils.configfile.ConfigFile()
        self.configfile.parse()

        ##
        # If there were missing items in the config file this is set to False.
        self.read_config = self._check_config()

        if cmdargs.stim_dir:
            self.set_stimulus_dir(cmdargs.stim_dir)
        if cmdargs.output_dir:
            self.set_output_dir(cmdargs.output_dir)
        if cmdargs.files:
            self.set_files(cmdargs.files)

        ##
        # The files that are selected.
        self.selected = []

        self[self.SMOOTH]        = cmdargs.smooth
        self[self.SMOOTHWIN]     = cmdargs.swin
        self[self.SMOOTHORDER]   = cmdargs.sorder
        self[self.THRESHOLD]     = cmdargs.threshold
        self[self.NTHRESHOLD]    = cmdargs.nthres
        self[self.DRAWSACCADES]  = cmdargs.draw_saccades
        self[self.COMPARE]       = cmdargs.compare
        self[self.ACTION]        = cmdargs.action
        self[self.EXTRACT_LEFT]  = cmdargs.extract_left
        self[self.EXTRACT_RIGHT] = cmdargs.extract_right
        self[self.STATUS]        = "ready"

    def readConfig(self):
        """Determine whether iSpector was able to read/parse the config file."""
        return self.read_config

    def config_dirs(self):
        """Obtain the map with common directories."""
        return self.configfile[utils.configfile.DIR]

    def stimulus_dir(self):
        """Get the stimulus directory."""
        return self.config_dirs()[utils.configfile.STIMDIR]

    def set_stimulus_dir(self, stimdir):
        """Set the stimulus directory."""
        self.config_dirs()[utils.configfile.STIMDIR] = stimdir

    def output_dir(self):
        """Get the output directory."""
        return self.config_dirs()[utils.configfile.OUTPUTDIR]

    def set_output_dir(self, outputdir):
        """Set the output directory."""
        self.config_dirs()[utils.configfile.OUTPUTDIR] = outputdir

    def file_dir(self):
        """Get the directory in which the last file was opened."""
        return self.config_dirs()[utils.configfile.FILEDIR]

    def set_file_dir(self, outputdir):
        """Set the output directory."""
        self.config_dirs()[utils.configfile.OUTPUTDIR] = outputdir

    def set_files(self, files):
        """Set the files on which iSpector operates."""
        self.configfile[utils.configfile.FILE_HIST] = list(files)

    def files(self):
        """Obtain the list of files on which iSpector operates."""
        return self.configfile[utils.configfile.FILE_HIST]

    def _check_config(self):
        """Check the config file, to see whether the expected member are present.

        This function can fail if a necessary element of the expected data
        members isn't present. If it isn't, then this function should initialize
        it with a default value.
        @return This function returns true when there were no expected data members
        missing.
        """
        missing = False
        if utils.configfile.DIR not in self.configfile:
            self.configfile[utils.configfile.DIR] = utils.configfile.ConfigDir()
            missing = True

        if utils.configfile.FILE_HIST not in self.configfile:
            self.configfile[utils.configfile.FILE_HIST] = list()
            missing= True

        return not missing
