#!/usr/bin/env python

import numpy as np
from scipy.misc import imread
import scipy as sp

import arguments as cmdargs
import os.path
from eyeexperiment import EyeExperiment
from parseeyefile import parseEyeFile
from eyedata import EyeData 
from eyelog import LogEntry
import statusmessage as sm
import configfile 


from PyQt4 import QtGui, QtCore

#import matplotlib.cbook as cbook
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationBar
from matplotlib.figure import Figure

#
# line types used throughout this module
#
_leftl      = 'b-' #:lefteye
_rightl     = 'r-' #:righteye
_thresholdl = 'm--' #:theshold line
_smoothl    = 'g-' #:smoothed line
_startf     = 'ro' #:start fix line type
_endf       = 'go' #:end fix line type
_startsac   = 'rd' #:start saccade
_endsac     = 'gd' #:end saccade
_slogfix    = 'r+' #:start log fix
_elogfix    = 'g+' #:end log fix
_logfixcol  = 'm-' #:logged fixation color (for comparison with our fixations)

def gcd_iter(u, v):
    '''
    Compute greatest common denominator
    Source: http://rosettacode.org/wiki/Greatest_common_divisor#Iterative_Euclid_algorithm_10
    date: 12 nov 2015
    '''
    while v:
        u, v = v, u % v
    return abs(u)

class SignalPlotWidget(FigureCanvas):
    ''' A plot to create to visualize content within a Qt program '''
    
    def __init__(self, parent = None, figsize=(16,9), dpi=80):
        self.fig = Figure(figsize=figsize, dpi=dpi)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        self.axgazex = self.fig.add_subplot(311)
        self.axgazey = self.fig.add_subplot(312)
        self.axvelo  = self.fig.add_subplot(313)

    def setLabels(self):
        self.axgazex.set_title("Eyeposition and velocity")
        self.axgazex.set_ylabel("x(Cal units)")
        self.axvelo.set_xlabel("time(ms)")
        self.axgazey.set_ylabel("y(cal units)")
        self.axvelo.set_ylabel("velocity(calunits/ms)")

    def plotData(self, xgaze, ygaze, velo, time, threshold, linestyle=_leftl, thresholdstyle=_thresholdl):
        ''' plots the gaze data and velocity. Erases previous plots '''
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
    
    def clear(self):
        self.axgazex.cla()
        self.axgazey.cla()
        self.axvelo.cla()

    def plotSmoothed(self, smoothed_velo, time, linestyle = _smoothl):
        ''' Plots the smoothed velocity '''
        self.axvelo.plot(time[0:len(smoothed_velo)], smoothed_velo, linestyle)

    def plotFixations(self, fix, xgaze, ygaze, time, startfixstyle=_startf, endfixstyle= _endf):
        '''
        Plots fixations marks where the begin and end over the gazedata, thus
        plot those first
        '''
        self.axgazex.plot(
                 time[fix == EyeData._sf], xgaze[fix == EyeData._sf], startfixstyle,
                 time[fix == EyeData._ef], xgaze[fix == EyeData._ef], endfixstyle
                 )
        self.axgazey.plot(
                 time[fix == EyeData._sf], ygaze[fix == EyeData._sf], startfixstyle,
                 time[fix == EyeData._ef], ygaze[fix == EyeData._ef], endfixstyle
                 )

    def plotSaccades(self, sacvec, xgaze, ygaze, times, startsacstyle=_startsac, endsacstyle=_endsac):
        ''' Plot marks where saccades start and end '''
        boolvecstart = sacvec == EyeData._sf
        boolvecend   = sacvec == EyeData._ef

        # mark x gaze
        self.axgazex.plot(times[boolvecstart], xgaze[boolvecstart], startsacstyle)
        self.axgazex.plot(times[boolvecend]  , xgaze[boolvecend]  , endsacstyle)

        # mark y gaze
        self.axgazey.plot(times[boolvecstart], ygaze[boolvecstart], startsacstyle)
        self.axgazey.plot(times[boolvecend]  , ygaze[boolvecend]  , endsacstyle)

class GazePlotWidget(FigureCanvas):
    
    def __init__(self, parent=None, dpi=100, figsize=(16,9)):
        figsize = None
        self.fig = Figure(figsize=figsize, dpi=dpi )

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        self.axgaze = self.fig.add_subplot(111)

    def clear(self):
        self.axgaze.cla()

    def plotGazePicture(self, picture, stimdir=None, lx=None, ly=None, rx=None, ry=None):
        '''
        Plots gaze over the stimulus. If the stimulus can't be read
        it just plots the gaze, and an IOError will be returned

        @param Picture name of the picture of the stimulus
        @param stimdir optional dirname to find the stimulus
        @param lx left eye x coordinate
        @param ly left eye y coordinate
        @param rx right eye x coordinate
        @param ry right eye y coordinate
        @return An caught exception or None if no error occured.
        '''
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
        
        if lx != None and ly != None:
            self.axgaze.plot(lx, ly, _leftl, zorder=1)
            self.axgaze.hold(True)
        if rx != None and ry != None:
            self.axgaze.plot(rx, ry, _rightl, zorder=1)
            self.axgaze.hold(True)

        return e1

class EyeOutput :
    '''
    This class uses an eyetrial to obtain the eyetracking data of
    one trial and is able to plot that data and generate the results.
    '''

    def __init__(self, eyedata, filename, smooth=True, compare=False):
        self._ed=eyedata
        #self.smooth = smooth
        self.stimfile = filename
        #self.compare=compare
        self.lgazetimes, self.rgazetimes    = eyedata.getTimes()
        # if only one of the right or left times is known set one to the other 
        if len(self.lgazetimes) == 0 and len(self.rgazetimes) > 0:
            self.lgazetimes = self.rgazetimes
        if len(self.rgazetimes) == 0 and len(self.lgazetimes) > 0:
            self.rgazetimes = self.lgazetimes
        self.xgazeleft,  self.ygazeleft     = eyedata.getLeft()
        self.xgazeright, self.ygazeright    = eyedata.getRight()
        if smooth:
            self.xgazelefts, self.ygazelefts= eyedata.getLeft(True)
            self.xgazerights,self.ygazerights=eyedata.getRight(True)
        self.fixl, self.fixr                = eyedata.getFixVecs()
        self.sacl, self.sacr                = eyedata.getSacVecs()
        self.velol, self.velor              = eyedata.getVelo(False)
        if smooth:
            self.velols, self.velors        = eyedata.getVelo(True)

    def plotLFixations(self):
        ''' plots the fixations as detected by an EyeData instance '''
        self.axlgazex.plot(
                 self.lgazetimes[self.fixl == self._ed._sf], self.xgazeleft[self.fixl == self._ed._sf], self._startf,
                 self.lgazetimes[self.fixl == self._ed._ef], self.xgazeleft[self.fixl == self._ed._ef], self._endf
                 )
        self.axlgazey.plot(
                 self.lgazetimes[self.fixl == self._ed._sf], self.ygazeleft[self.fixl == self._ed._sf], self._startf,
                 self.lgazetimes[self.fixl == self._ed._ef], self.ygazeleft[self.fixl == self._ed._ef], self._endf
                 )

    def _plotLGaze(self, smooth):
        self.lplot = plt.figure(2)
        self.axlgazex = self.lplot.add_subplot(311)
        self.axlgazex.set_title("Left eye, eyeposition and velocity")
        self.axlgazex.set_ylabel("x(Calibration units)")

        self.axlgazex.plot(self.lgazetimes, self.xgazeleft)
        #if smooth == True:
        #    plt.plot(self.lgazetimes, self.xgazelefts,'g-')
        
        self.axlgazey = self.lplot.add_subplot(312)
        self.axlgazey.set_ylabel("y(calibration units)")
        self.axlgazey.plot(self.lgazetimes, self.ygazeleft)
        #if smooth == True:
        #    self.axlgazey.plot(self.lgazetimes, self.ygazelefts,'g-')
        
        self.axlvelo = self.lplot.add_subplot(313)
        self.axlvelo.set_xlabel("time(ms)")
        self.axlvelo.set_ylabel("velocity(calunits/ms)")
        velline = np.ones(len(self.lgazetimes)-1) * self._ed.getThreshold()[0]
        self.axlvelo.plot(self.lgazetimes[1:len(self.lgazetimes)], self.velol, 'b-',
                 self.lgazetimes[1:len(self.lgazetimes)], velline, 'b--'
                 )
        if smooth == True:
            self.axlvelo.plot(self.lgazetimes[1:len(self.lgazetimes)], self.velols,'g-')
    
    def plotRFixations(self):
        ''' plots the fixations as detected by an EyeData instance '''
        self.axrgazex.plot(
                 self.rgazetimes[self.fixr == self._ed._sf], self.xgazeright[self.fixr == self._ed._sf], self._startf,
                 self.rgazetimes[self.fixr == self._ed._ef], self.xgazeright[self.fixr == self._ed._ef], self._endf
                 )
        self.axrgazey.plot(
                 self.rgazetimes[self.fixr == self._ed._sf], self.ygazeright[self.fixr == self._ed._sf], self._startf,
                 self.rgazetimes[self.fixr == self._ed._ef], self.ygazeright[self.fixr == self._ed._ef], self._endf
                 )

    def plotLSaccades(self):
        ''' plots the saccades for the left eye.'''
        self._plotSaccades(self.axlgazex, self.axlgazey, self.sacl, self.xgazeleft, self.ygazeleft)
    
    def plotRSaccades(self):
        ''' plots the saccades for the right eye.'''
        self._plotSaccades(self.axrgazex, self.axrgazey, self.sacr, self.xgazeright, self.ygazeright)
    
    def _plotSaccades(self, axesx, axesy, sacvec, xgaze, ygaze):
        ''' Plot marks where saccades start and end '''
        boolvecstart = sacvec == self._ed._sf
        boolvecend   = sacvec == self._ed._ef

        # mark x gaze
        axesx.plot(self.rgazetimes[boolvecstart], xgaze[boolvecstart], self._startsac)
        axesx.plot(self.rgazetimes[boolvecend]  , xgaze[boolvecend]  , self._endsac)

        # mark y gaze
        axesy.plot(self.rgazetimes[boolvecstart], ygaze[boolvecstart], self._startsac)
        axesy.plot(self.rgazetimes[boolvecend]  , ygaze[boolvecend]  , self._endsac)
    
    def _plotRGaze(self, smooth):
        ''' Plot the right gaze.
        '''
        self.rplot = plt.figure(3)
        self.axrgazex = self.rplot.add_subplot(311)
        self.axrgazex.set_title("Right eye, eyeposition and velocity")
        self.axrgazex.set_ylabel("x(Calibration units)")
        self.axrgazex.plot(self.rgazetimes, self.xgazeright, 'r-')
        #if smooth == True:
        #    self.axrgazex.plot(self.rgazetimes, self.xgazerights,'g-')
                    
        self.axrgazey = self.rplot.add_subplot(312)
        self.axrgazey.set_ylabel("y(Calibration units)")
        self.axrgazey.plot(self.rgazetimes, self.ygazeright, 'r-')
        #if smooth == True:
        #    self.axrgazey.plot(self.rgazetimes, self.ygazerights,'g-')
                    
        self.axrvelo = self.rplot.add_subplot(313)
        self.axrvelo.set_xlabel("time(ms)")
        self.axrvelo.set_ylabel("velocity(calunits/ms)")
        velline = np.ones(len(self.rgazetimes)-1) * self._ed.getThreshold()[1] 
        self.axrvelo.plot(self.rgazetimes[0:len(self.rgazetimes)-1], self.velor, 'b-',
                 self.lgazetimes[1:len(self.rgazetimes)], velline, 'b--')
        if smooth == True:
            self.axrvelo.plot(self.rgazetimes[0:len(self.rgazetimes)-1], self.velors,'g-')

#    def compareLeft(self):
#        ''' Plots start and end fixation marks as logged.
#        '''
#        starttimes = []
#        endtimes = []
#        xs = []
#        ys = []
#        for fix in self._ed.logfixl:
#            starttimes.append(fix.eyetime)
#            endtimes.append(fix.eyetime + fix.duration)
#            xs.append(fix.x)
#            ys.append(fix.y)
#            time = np.array([fix.eyetime, fix.eyetime+fix.duration])
#            plt.subplot(311)
#            plt.plot(time, np.ones(2)*fix.x, self._logfixcol)
#            plt.subplot(312)
#            plt.plot(time, np.ones(2)*fix.y, self._logfixcol)
#        plt.subplot(311)
#        plt.plot(starttimes, xs, self._slogfix)
#        plt.plot(endtimes, xs, self._elogfix)
#        plt.subplot(312)
#        plt.plot(starttimes, ys, self._slogfix)
#        plt.plot(endtimes, ys, self._elogfix)
#
#    def compareRight(self): 
#        ''' Plots start and end fixation marks as logged.
#            This allows for a visual comparison.
#        '''
#        starttimes = []
#        endtimes = []
#        xs = []
#        ys = []
#        for fix in self._ed.logfixr:
#            starttimes.append(fix.eyetime)
#            endtimes.append(fix.eyetime + fix.duration)
#            xs.append(fix.x)
#            ys.append(fix.y)
#            time = np.array([fix.eyetime, fix.eyetime+fix.duration])
#            plt.subplot(311)
#            plt.plot(time, np.ones(2)*fix.x, self._logfixcol)
#            plt.subplot(312)
#            plt.plot(time, np.ones(2)*fix.y, self._logfixcol)
#        plt.subplot(311)
#        plt.plot(starttimes, xs, self._slogfix)
#        plt.plot(endtimes, xs, self._elogfix)
#        plt.subplot(312)
#        plt.plot(starttimes, ys, self._slogfix)
#        plt.plot(endtimes, ys, self._elogfix)
            
    def _plotTrial(self):
        try:
            img = imread(os.path.join(cmdargs.ARGS.stim_dir, self.stimfile))
        except IOError:
            img = imread( self.stimfile)
            
        fig1 = plt.figure(1);
        leftgazex, leftgazey   = self._ed.getLeft()
        rightgazex, rightgazey = self._ed.getRight()

        plt.plot(leftgazex,  leftgazey,  self._leftl, zorder=1)
        plt.plot(rightgazex, rightgazey, self._rightl,zorder=1)

        plt.imshow(img, zorder=0)

    def show(self):
        ''' Plot the eyedata and show it to the user.'''
        self._plotTrial()
        plt.show()


class ExamineDataModel(object):

    ''' the model for the data to be presented '''

    def __init__(self, files, mainwin):
        ''' the eyedata takes a number of files '''
        self.files      = files
        self.MAINWIN    = mainwin
        self.fileindex  = 0
        self.trialindex = 0
        self.eyedata    = None
        if not self.loadEyeFile():
            return
        self._loadEyeData()

    def loadEyeFile(self):
        ''' load the eyefile '''
        fid = self.files[self.fileindex]
        pr = parseEyeFile(fid)
        entries = pr.getEntries()
        if not entries:
            errors = pr.getErrors()
            for i in errors:
                self.MAINWIN.reportStatus(i[2], i[0] + ':' + str(i[1]))
            return False

        MODEL = self.MAINWIN.getModel()[0] # ignore the controller in the tuple

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
            return

        self.experiment = EyeExperiment(entries)
        self.trials     = self.experiment.trials

        return True

    def _loadEyeData(self):
        ''' Load eyedata '''
        trial = self.trials[self.trialindex]
        # We only want to read the model thus no need to get the controller
        MM = self.MAINWIN.getModel()[0]
        thres   = MM[MM.THRESHOLD]
        nthres  = MM[MM.NTHRESHOLD]
        smooth  = MM[MM.SMOOTH]
        win     = MM[MM.SMOOTHWIN]
        order   = MM[MM.SMOOTHORDER]

        self.eyedata = EyeData(thres, nthres, smooth, win, order)
        self.eyedata.processTrial(self.trials[self.trialindex])

class ExamineDataController(object):
    
    ''' Controls the model of data '''

    def __init__(self, model):
        self.model = model
        if not self.model.loadEyeFile():
            return
        self.setTrialIndex(0)

    def reload(self):
        self.model._loadEyeData()

    def setFileIndex(self, n):
        '''
        Set the index of the file to display
        '''
        self.model.fileindex = n
        if self.model.fileindex < 0:
            self.model.fileindex = 0
        elif self.model.fileindex >= len(self.model.files):
            self.model.fileindex = len(self.model.files) - 1
        # load new eyefile 
        if not self.model.loadEyeFile():
            return
        # Make sure no invalid trial is selected
        self.setTrialIndex(self.model.trialindex)

    def setTrialIndex(self, n):
        '''
        Set the index of the trial to display
        This should be the only function that makes
        the data model load the eyedata, since this is
        probably the most expensive function.
        '''
        self.model.trialindex = n
        if self.model.trialindex < 0:
            self.model.trialindex = 0
        elif self.model.trialindex >= len(self.model.trials):
            self.model.trialindex = len(self.model.trials) - 1
        self.model._loadEyeData()

    def nextTrial(self):
        ''' present next trial even if in new file '''
        if len(self.model.trials) <= self.model.trialindex + 1:
            self.setFileIndex(self.model.fileindex + 1)
            self.setTrialIndex(0)
            return
        self.setTrialIndex(self.model.trialindex + 1)
    
    def prevTrial(self):
        ''' Present previous trial even if in new file '''
        if self.model.trialindex - 1 < 0:
            self.setFileIndex(self.model.fileindex - 1)
            self.setTrialIndex(len(self.model.trials) - 1)
            return
        self.setTrialIndex(self.model.trialindex - 1)

class ExamineEyeDataWidget(QtGui.QWidget):
    '''
    Display a the EyeData of a number of files
    '''
    LEFT_EYE_STR   = "left eye signal"
    RIGHT_EYE_STR  = "right eye signal"
    GAZE_PLOT_STR  = "Gaze plot"

    def __init__(self, files, parent) :
        super(ExamineEyeDataWidget, self).__init__(parent=parent, flags=QtCore.Qt.Window)
        self.MAINWINDOW = parent
        self.MODEL      = ExamineDataModel(files, parent)
        if not self.MODEL.eyedata:
            QtGui.QApplication.postEvent(self, QtGui.QCloseEvent())
            return
        self.controller = ExamineDataController(self.MODEL)
        self._initGui()
        self.updateFromModel()

    def hasValidData(self):
        return self.MODEL.eyedata != None

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

        self.lsignal = SignalPlotWidget()
        toolbar = NavigationBar(self.lsignal, self)
        self.tabview.addTab(self._createPlotVBox(self.lsignal, toolbar),
                            self.LEFT_EYE_STR
                            )
        
        self.rsignal = SignalPlotWidget()
        toolbar = NavigationBar(self.rsignal, self)
        self.tabview.addTab(self._createPlotVBox(self.rsignal, toolbar), self.RIGHT_EYE_STR)

        self.gazeplot= GazePlotWidget()
        toolbar = NavigationBar(self.gazeplot, self)
        self.tabview.addTab(self._createPlotVBox(self.gazeplot, toolbar), self.GAZE_PLOT_STR)

        #self.gazeplot = GazePlotWidget()
        #self.tabview.addTab(self.gazeplot, self.GAZE_PLOT_STR)
        
        self.fileslider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.fileslider.setMinimum(1)
        self.fileslider.setToolTip("File slider")
        self.trialslider= QtGui.QSlider(QtCore.Qt.Horizontal)
        self.trialslider.setMinimum(1)
        self.trialslider.setToolTip("Trial slider")
        
        self.fileslider.sliderReleased.connect(self.fileSliderChanged)
        self.trialslider.sliderReleased.connect(self.trialSliderChanged)

        grid.addWidget(self.trialslider, 1, 1)
        grid.addWidget(self.fileslider , 2, 1)
        
        self.setLayout(grid)
        self.show()
        self.leftplot = None
        self.rightplot= None

    def keyPressEvent(self, event):
        ''' Capture F5 to reload with current settings. '''
        key = event.key()
        if key == QtCore.Qt.Key_F5:
            self.controller.reload()
            self.updateFromModel()
        return super(ExamineEyeDataWidget, self).keyPressEvent(event)

    def _createPlotVBox(self, widget, toolbar):
        w = QtGui.QWidget()
        l = QtGui.QVBoxLayout()
        l.addWidget(widget, 10)
        l.addWidget(toolbar, 0, QtCore.Qt.AlignLeft)
        w.setLayout(l)
        return w

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
    
    def updatePlots(self):
        assert(self.MODEL.eyedata)
        ed = self.MODEL.eyedata
        trial = self.MODEL.trials[self.MODEL.trialindex]
        MM = self.MAINWINDOW.getModel()[0] #ignore the controller
        lt, rt = ed.getTimes()
        thresl, thresr = ed.getThreshold()
        times = None
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

        stimdir = MM[MM.DIRS][configfile.STIMDIR]

        self.gazeplot.plotGazePicture(trial.stimulus, stimdir, lx, ly, rx, ry)

        self.lsignal.draw()
        self.rsignal.draw()
        self.gazeplot.draw()

    def updateTitle(self):
        filename = os.path.split(self.MODEL.files[self.MODEL.fileindex])[1]
        trial = self.MODEL.trialindex + 1
        title = "File {0}: trial {1}".format(filename, trial)
        if not (self.MODEL.eyedata.hasRightGaze() or self.MODEL.eyedata.hasLeftGaze() ):
            title += " (NO EYE DATA IN TRIAL)"
        self.setWindowTitle(title)

    def updateFromModel(self):
        self.updateSliders()
        self.updatePlots()
        self.updateTitle()

    def trialSliderChanged(self):
        val = self.trialslider.value()
        self.controller.setTrialIndex(val - 1)
        self.updateFromModel()

    def fileSliderChanged(self):
        val = self.fileslider.value()
        self.controller.setFileIndex(val - 1)
        self.updateFromModel()

    def nextTrial(self):
        self.controller.nextTrial()
        self.updateFromModel()
    
    def prevTrial(self):
        self.controller.prevTrial()
        self.updateFromModel()
