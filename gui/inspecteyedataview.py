#!/usr/bin/env python

##
# \file inspecteyedataview.py
#
# \todo make it possible to compare fixations

import numpy as np
from scipy.misc import imread
import scipy as sp

#import arguments as cmdargs
import os.path
from log.eyeexperiment import EyeExperiment
from log.parseeyefile import parseEyeFile
from log.eyedata import EyeData 
from log.eyelog import LogEntry
import datamodel as dm
import dataview  as dv
import statusmessage as sm
import utils.configfile 


from PyQt4 import QtGui, QtCore

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
# Apparently NavigationToolbar2QTAgg is renamed in newer versions 
# so much for backward compatibility...
try :
    from matplotlib.backends.backend_qt4agg import\
            NavigationToolbar2QTAgg as NavigationBar
except ImportError as e:
    from matplotlib.backends.backend_qt4agg import\
            NavigationToolbar2QT as NavigationBar

from matplotlib.figure import Figure

#
# line types used throughout this module
#
_leftl      = 'b-'  #:lefteye
_rightl     = 'r-'  #:righteye
_thresholdl = 'm--' #:threshold line
_smoothl    = 'g-'  #:smoothed line
_startf     = 'ro'  #:start fix line type
_endf       = 'go'  #:end fix line type
_startsac   = 'rd'  #:start saccade
_endsac     = 'gd'  #:end saccade
_slogfix    = 'r+'  #:start log fix
_elogfix    = 'g+'  #:end log fix
_logfixcol  = 'm-'  #:logged fixation color (for comparison with our fixations)

def gcd_iter(u, v):
    '''
    Compute greatest common denominator
    Source: http://rosettacode.org/wiki/Greatest_common_divisor#Iterative_Euclid_algorithm_10
    date: 12 nov 2015
    '''
    while v:
        u, v = v, u % v
    return abs(u)

##
# A plot to create to visualize content within a Qt program
#
# The SignalPlotWidget represents a canvas that demonstrates 3
# plots one for the X coordinate component in the eyesignal
# one for the Y component and one for the velocity component
#
class SignalPlotWidget(FigureCanvas):
    
    ##
    # Construct a SignalPlotWidget
    #
    # \param parent is the QtWidget that will be the parent of this widget.
    # \param figsize a suggested figure size for the signal plot
    # \param dpi a higher dpi will make a nicer plot, however will also take
    # longer to draw
    def __init__(self, parent = None, figsize=None, dpi=80):
        self.fig = Figure(figsize=figsize, dpi=dpi)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        # matplotlib axis for the x signal
        self.axgazex = self.fig.add_subplot(311)
        # matplotlib axis for the y signal
        self.axgazey = self.fig.add_subplot(312)
        # matplotlib axis for the velocity
        self.axvelo  = self.fig.add_subplot(313)

    ##
    # puts the labels on the axis of the plots.
    def setLabels(self):
        self.axgazex.set_title("Eyeposition and velocity")
        self.axgazex.set_ylabel("x(Cal units)")
        self.axvelo.set_xlabel("time(ms)")
        self.axgazey.set_ylabel("y(cal units)")
        self.axvelo.set_ylabel("velocity(calunits/ms)")

    ##
    # Plots the gaze data and velocity. Erases previous plots.
    #
    # Plots the signals, <b>Note</b> that all numpy arrays should be of the
    # same length only the velocity might be (one) shorter than the rest.
    #
    # \param xgaze numpy array with the x gaze signal
    # \param ygaze numpy array with the y gaze signal
    # \param velo numpy array with the velocity of the eye
    # \param time the times that belong to the 
    # \param threshold a value that represents the treshold between a fixation
    #        and a saccade
    # \param linestyle the linestyle that will be used for the signal.
    # \param thresholdstyle the linestyle for the threshold.
    def plotData(self, xgaze, ygaze, velo, time, threshold, linestyle=_leftl, thresholdstyle=_thresholdl):
        self.axgazex.hold(False)
        self.axgazey.hold(False)
        self.axvelo.hold(False)
        self.axgazex.plot(time, xgaze, linestyle)
        self.axgazey.plot(time, ygaze, linestyle)
        self.axvelo.plot(time[0:len(velo)], velo, linestyle)
        self.axgazex.hold(True)
        self.axgazey.hold(True)
        self.axvelo.hold(True)
        
        # create threshold
        timestart = time[0]
        timeend   = time[len(time)-1]
        thres     = np.ones(time.size) * threshold
        self.axvelo
        self.setLabels()
        self.axvelo.plot(time, thres, thresholdstyle)
    ##
    # clears the all axis
    def clear(self):
        self.axgazex.cla()
        self.axgazey.cla()
        self.axvelo.cla()

    ##
    # Plots the smoothed velocity.
    def plotSmoothed(self, smoothed_velo, time, linestyle = _smoothl):
        self.axvelo.plot(time[0:len(smoothed_velo)], smoothed_velo, linestyle)

    ##
    # Plots fixations marks where the begin and end over the gazedata, thus
    # plot those first.
    def plotFixations(self, fix, xgaze, ygaze, time, startfixstyle=_startf, endfixstyle= _endf):
        self.axgazex.plot(
                 time[fix == EyeData._sf], xgaze[fix == EyeData._sf], startfixstyle,
                 time[fix == EyeData._ef], xgaze[fix == EyeData._ef], endfixstyle
                 )
        self.axgazey.plot(
                 time[fix == EyeData._sf], ygaze[fix == EyeData._sf], startfixstyle,
                 time[fix == EyeData._ef], ygaze[fix == EyeData._ef], endfixstyle
                 )

    ##
    # Plot marks where saccades start and end.
    def plotSaccades(self, sacvec, xgaze, ygaze, times, startsacstyle=_startsac, endsacstyle=_endsac):
        boolvecstart = sacvec == EyeData._sf
        boolvecend   = sacvec == EyeData._ef

        # mark x gaze
        self.axgazex.plot(times[boolvecstart], xgaze[boolvecstart], startsacstyle)
        self.axgazex.plot(times[boolvecend]  , xgaze[boolvecend]  , endsacstyle)

        # mark y gaze
        self.axgazey.plot(times[boolvecstart], ygaze[boolvecstart], startsacstyle)
        self.axgazey.plot(times[boolvecend]  , ygaze[boolvecend]  , endsacstyle)

##
# This is a Gaze plot over the stimulus
#
# The GazePlotWidget plots the signal of the left and or right eye
# over the visual stimulus if it is present.
#
class GazePlotWidget(FigureCanvas):
    
    ##
    # Inits the gaze plot widget
    #
    def __init__(self, parent=None, dpi=100, figsize=(16,9)):
        #figsize = None
        ## a matplotlib figure
        self.fig = Figure(figsize=figsize, dpi=dpi )

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        self.axgaze = self.fig.add_subplot(111)
    
    ##
    # clear the plot/axis
    def clear(self):
        self.axgaze.cla()

    ##
    # Plots gaze over the stimulus. If the stimulus can't be read
    # it just plots the gaze, and an IOError will be returned
    #
    # \param Picture name of the picture of the stimulus
    # \param stimdir optional dirname to find the stimulus
    # \param lx left eye x coordinate
    # \param ly left eye y coordinate
    # \param rx right eye x coordinate
    # \param ry right eye y coordinate
    #
    # \return A caught exception or None if no error occured.
    def plotGazePicture(self, picture, stimdir=None, lx=None, ly=None, rx=None, ry=None):
        img = None
        abspath = None
        e1 = None
        self.axgaze.hold(False)
        self.clear()

        if stimdir:
            abspath = os.path.join(stimdir, picture)
            self.axgaze.hold(True)
        if stimdir:
            try:
                # try absolute path
                img = imread(abspath)
            except IOError as e1:
                pass

        if img == None:
            try:
                img = imread(picture)
            except IOError as e1:
                pass

        if img == None:
            msg = "Unable to load: " + picture + "Did you set the stimulus directory?"
            p = self
            last = None
            while p:
                last = p
                p = p.parent()
            last.reportStatus(sm.StatusMessage.warning, msg)
            
        else:
            s = img.shape
            g = gcd_iter(s[0], s[1])
            #self.figure.set_size_inches(s[0]/g, s[1]/g)
            self.axgaze.set_ylim(s[0], 0)
            self.axgaze.set_xlim(0, s[1])
            self.axgaze.imshow(img, zorder=0, interpolation='nearest')
            #self.figure.figaspect(img.size)
        
        if not lx is None and not ly is None:
            self.axgaze.plot(lx, ly, _leftl, zorder=1)
            self.axgaze.hold(True)
        if not rx is None and not ry is None:
            self.axgaze.plot(rx, ry, _rightl, zorder=1)
            self.axgaze.hold(True)

        return e1

##
# A plot to create to visualize pupilsize within a Qt program
#
# The PupilPlotWidget represents a canvas that demonstrates 3
# plots one for the X coordinate component in the eyesignal
# one for the Y component and one for the velocity component
#
class PupilPlotWidget(FigureCanvas):
    
    ##
    # Construct a PupilPlotWidget
    #
    # \param parent is the QtWidget that will be the parent of this widget.
    # \param figsize a suggested figure size for the signal plot
    # \param dpi a higher dpi will make a nicer plot, however will also take
    # longer to draw
    def __init__(self, parent = None, figsize=None, dpi=80):
        self.fig = Figure(figsize=figsize, dpi=dpi)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        # matplotlib axis for the x signal
        self.axpupilleft = self.fig.add_subplot(311)
        # matplotlib axis for the y signal
        self.axpupilright= self.fig.add_subplot(312)
        # matplotlib axis for the velocity
        self.axpupilleftright= self.fig.add_subplot(313)

    def clear(self):
        self.axpupilleft.cla()
        self.axpupilright.cla()
        self.axpupilleftright.cla()

    def plotPupil(self, times, lpup, rpup):
        self.clear()
        print (times[0:5])
        print (lpup[0:5])
        if len(lpup) > 0:
            self.axpupilleft.plot(times, lpup, _leftl)
        if len(rpup) > 0:
            self.axpupilright.plot(times, rpup, _rightl)
        if len(rpup) > 0 and len (lpup) > 0:
            self.axpupilleftright.plot(
                times, lpup, _leftl,
                times, rpup, _rightl
                )

##
# Displays a tabbed window with multiple signals
#
# This is the CustomDataView of InspectDataView.
class TabbedSignalView(dv.CustomDataView, QtGui.QWidget):
    
    ## tile for the tab of the left eye
    LEFT_EYE_STR   = "left eye signal"
    ## tile for the tab of the right eye
    RIGHT_EYE_STR  = "right eye signal"
    ## tile for the tab of the gaze plot
    GAZE_PLOT_STR  = "Gaze plot"
    ## title for the tab of the pupil size
    PUPIL_PLOT_STR = "Pupil size plot"

    ##
    # inits a TabbedSignalView
    #
    # \param model and instance of ExamineDataModel
    # \param parent
    def __init__(self, model, parent=None ):
        super(TabbedSignalView, self).__init__(parent=parent)
        ##
        # An instance of ExamineDataModel
        self.MODEL      = model
        ##
        # A reference to the iSpector main window
        self.MAINWINDOW = model.getMainWindow()
        self._initGui()
        self.setContentsMargins(0,0,0,0)

    def _initGui(self):
        # create a layout witout spacing
        # and add the layout to the widget
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0)
        tabview = QtGui.QTabWidget(parent=self)
        ## a QTabWidget
        self.tabview = tabview
        layout.addWidget(tabview)
        self.setLayout(layout)

        ## A SignalPlotWidget for the left eye.
        self.lsignal = SignalPlotWidget()
        toolbar = NavigationBar(self.lsignal, self)
        self.tabview.addTab(self._createPlotVBox(self.lsignal, toolbar),
                            self.LEFT_EYE_STR
                            )
        
        ## A SignalPlotWidget for the right eye.
        self.rsignal = SignalPlotWidget()
        toolbar = NavigationBar(self.rsignal, self)
        self.tabview.addTab(self._createPlotVBox(self.rsignal, toolbar),
                            self.RIGHT_EYE_STR
                            )

        ## A GazePlotWidget that shows the gaze on the stimulus
        self.gazeplot= GazePlotWidget(self)
        toolbar = NavigationBar(self.gazeplot, self)
        self.tabview.addTab(self._createPlotVBox(self.gazeplot, toolbar),
                            self.GAZE_PLOT_STR
                            )
        
        ## A PupilPlotWidget that shows the pupilsize over time
        self.pupilplot = PupilPlotWidget()
        toolbar = NavigationBar(self.pupilplot, self)
        self.tabview.addTab(self._createPlotVBox(self.pupilplot,toolbar),
                            self.PUPIL_PLOT_STR
                            )

    ##
    # One tab contains a vertical box with a FigureCanvas and a Matplotlib toolbar.
    #
    # This function helps creating such a widget with embedded Matplotlib canvas and toolbar
    # in a QVBoxLayout.
    def _createPlotVBox(self, widget, toolbar):
        w = QtGui.QWidget()
        l = QtGui.QVBoxLayout()
        l.addWidget(widget, 10)
        l.addWidget(toolbar, 0, QtCore.Qt.AlignLeft)
        w.setLayout(l)
        return w

    ##
    # Calls updatePlots, that is everything this CustomDataView should do.
    def updateFromModel(self):
        # updates all views.
        self.updatePlots()

    ##
    # Repaints all four plots
    #
    def updatePlots(self):
        assert(self.MODEL.eyedata)
        ed      = self.MODEL.eyedata
        trial   = self.MODEL.trials[self.MODEL.trialindex]
        MM      = self.MAINWINDOW.getModel()[0] #ignore the controller
        lt, rt  = ed.getTimes()
        thresl, thresr = ed.getThreshold()
        pupl, pupr = ed.getPupilSize()
        times   = None
        if len(lt) > 0:
            times = lt
        else:
            times = rt
        
        fixl, fixr  = ed.getFixVecs()
        sacl, sacr  = ed.getSacVecs()

        if ed.hasLeftGaze():
            x,y = ed.getLeft()
            v   = ed.getLeftVelocity()         
            self.lsignal.plotData(x, y, v, times, thresl, _leftl)
            if MM[MM.SMOOTH]:
                sv = ed.getLeftVelocity(True)
                self.lsignal.plotSmoothed(sv, times, _smoothl)
            if MM[MM.DRAWSACCADES]:
                self.lsignal.plotSaccades(sacl, x, y, times)
            else:
                self.lsignal.plotFixations(fixl, x, y, times)
        else:
            self.lsignal.clear()
        if ed.hasRightGaze():
            x,y = ed.getRight()
            v   = ed.getRightVelocity()         
            self.rsignal.plotData(x, y, v, times, thresr, _rightl)
            if MM[MM.SMOOTH]:
                sv = ed.getRightVelocity(True)
                self.rsignal.plotSmoothed(sv, times, _smoothl)
            if MM[MM.DRAWSACCADES]:
                self.rsignal.plotSaccades(sacr, x, y, times)
            else:
                self.rsignal.plotFixations(fixr, x, y, times)
        else:
            self.rsignal.clear()

        lx, ly = ed.getLeft()
        rx, ry = ed.getRight()

        stimdir = MM[MM.DIRS][utils.configfile.STIMDIR]

        self.gazeplot.plotGazePicture(trial.stimulus, stimdir, lx, ly, rx, ry)

        self.pupilplot.plotPupil(times, pupl, pupr)

        self.lsignal.draw()
        self.rsignal.draw()
        self.gazeplot.draw()
        self.pupilplot.draw()

    def showEvent(self, event):
        super(TabbedSignalView, self).showEvent(event)
        margins = self.getContentsMargins()
        lay = self.layout()
        print "in show event with margins is {0} layout.spacing = {1}".format(str(margins), str(lay.spacing()))
        

##
# Display a the EyeData of a number of files
# 
# The InspectEyeDataView is a widget that helps inspecting the
# the Signals of the eye movement. The Signal is split in a
# X signal, a Y signal and over those two signals the velocity
# is computed. It can optionally smooth the data. New values
# for the fixations will be fitted to the smoothed signal instead
# of the rawsignal
#
# The InspectEyeDataView helps, because it displays those signals
# Therefore this widget is mostly helpfull in examining the quality
# of the data. Also it is helpfull in determining the most proper
# values for the smoothing parameters, so you can see what
# fixations iSpector will determine in the signal.
# 
class InspectEyeDataView(dv.DataView):
    
    ##
    # inits the InspectEyeDataView and checks whether the data is valid.
    #
    # \param model The model of the data must be a ExamineDataModel
    # \param controller the controller for the view.
    # \param parent passed to QtWidget.__init__
    def __init__(self, model, controller, parent=None) :
        super(InspectEyeDataView, self).__init__(model,
                                                 controller,
                                                 parent
                                                 )
        if not self.hasValidData():
            model.getMainWindow().reportStatus(StatusMessage.error, "Invalid Data...")
            QtGui.QApplication.postEvent(self, QtGui.QCloseEvent())
            return
    
    ##
    # test whether the model contains valid data
    def hasValidData(self):
        return self.MODEL.hasValidData()
    
    ##
    # this creates the tabbed signal view widget
    def initCustomWidget(self):
        ##
        # custom_widget is a TabbedSignalView that allows inspection of
        # eyedata.
        self.custom_widget = TabbedSignalView(self.MODEL)


