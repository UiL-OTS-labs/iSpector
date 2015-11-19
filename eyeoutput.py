#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
from scipy.misc import imread
import scipy as sp
import matplotlib.cbook as cbook
import arguments as cmdargs
import os.path


# gives nice gimmicks to save some extra nice output pictures.
_HAVE_CAIRO = False
try:
    import cairo as c
    _HAVE_CAIRO = True
except ImportError as e:
    print e

class EyeOutput :

    '''
    This class uses an eyetrial to obtain the eyetracking data of
    one trial and is able to plot that data and generate the results.
    '''

    #line types 
    _leftl      = 'b-' #:lefteye
    _rightl     = 'r-' #:righteye
    _smoothl    = 'g-' #:smoothed line
    _startf     = 'ro' #:start fix line type
    _endf       = 'go' #:end fix line type
    _startsac   = 'rd' #:start saccade
    _endsac     = 'gd' #:end saccade
    _slogfix    = 'r+' #:start log fix
    _elogfix    = 'g+' #:end log fix
    _logfixcol  = 'm-' #:logged fixation color (for comparison with our fixations)

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

    def compareLeft(self):
        ''' Plots start and end fixation marks as logged.
        '''
        starttimes = []
        endtimes = []
        xs = []
        ys = []
        for fix in self._ed.logfixl:
            starttimes.append(fix.eyetime)
            endtimes.append(fix.eyetime + fix.duration)
            xs.append(fix.x)
            ys.append(fix.y)
            time = np.array([fix.eyetime, fix.eyetime+fix.duration])
            plt.subplot(311)
            plt.plot(time, np.ones(2)*fix.x, self._logfixcol)
            plt.subplot(312)
            plt.plot(time, np.ones(2)*fix.y, self._logfixcol)
        plt.subplot(311)
        plt.plot(starttimes, xs, self._slogfix)
        plt.plot(endtimes, xs, self._elogfix)
        plt.subplot(312)
        plt.plot(starttimes, ys, self._slogfix)
        plt.plot(endtimes, ys, self._elogfix)

    def compareRight(self): 
        ''' Plots start and end fixation marks as logged.
            This allows for a visual comparison.
        '''
        starttimes = []
        endtimes = []
        xs = []
        ys = []
        for fix in self._ed.logfixr:
            starttimes.append(fix.eyetime)
            endtimes.append(fix.eyetime + fix.duration)
            xs.append(fix.x)
            ys.append(fix.y)
            time = np.array([fix.eyetime, fix.eyetime+fix.duration])
            plt.subplot(311)
            plt.plot(time, np.ones(2)*fix.x, self._logfixcol)
            plt.subplot(312)
            plt.plot(time, np.ones(2)*fix.y, self._logfixcol)
        plt.subplot(311)
        plt.plot(starttimes, xs, self._slogfix)
        plt.plot(endtimes, xs, self._elogfix)
        plt.subplot(312)
        plt.plot(starttimes, ys, self._slogfix)
        plt.plot(endtimes, ys, self._elogfix)
            
    def _plotTrial(self):
        try:
            img = imread(os.path.join(cmdargs.ARGS.stim_dir, self.stimfile))
        except IOError:
            img = imread(self.stimfile)
            
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

class FixationImage:

    '''Creates a png image of the fixations of a trial.'''
    leftline    = 0.0, 0.0, 1.0
    leftcircle  = 0.0, 0.0, 1.0, 0.4
    rightline   = 1.0, 0.0, 0.0
    rightcircle = 1.0, 0.0, 0.0, 0.4

    def __init__(self, eyetrial):
        self.image  = eyetrial.stimulus
        self.et     = eyetrial
        self.outpng = self._createOutputFile();
        self.surf   = c.ImageSurface.create_from_png(self.image)
        self.cr     = c.Context(self.surf)
        self.cr.set_line_width(1.0)
        self._makePaths()
        self._drawFixations()

    def _makePaths(self):
        if len(self.et.lfix) > 0:
            self.cr.set_source_rgb(*self.leftline)
            self._drawPath(self.et.lfix)
        if len(self.et.rfix) > 0:
            self.cr.set_source_rgb(*self.rightline)
            self._drawPath(self.et.rfix)

    def _drawPath(self, fixations):
        for f in fixations:
            if f is fixations[0]:
                self.cr.move_to(f.x, f.y)
            else:
                self.cr.line_to(f.x, f.y)
        self.cr.stroke()

    def _circle(self, x, y, r):
        self.cr.save()
        self.cr.translate(x, y)
        self.cr.arc(0, 0, r, 0.0, 2*3.141592654)
        self.cr.restore()

    def _drawFixations(self, devradius=15):
        '''
        draws the fixations
        @param devradius radius = fixationduration/devradius
        '''
    
        for f in self.et.lfix:
            radius = f.duration/devradius
            self.cr.set_source_rgb(*self.leftline)
            self._circle(f.x, f.y, radius)
            self.cr.stroke()
            self.cr.set_source_rgba(*self.leftcircle)
            self._circle(f.x, f.y, radius)
            self.cr.fill()
        for f in self.et.rfix:
            radius = f.duration/devradius
            self.cr.set_source_rgb(*self.rightline)
            self._circle(f.x, f.y, radius)
            self.cr.stroke()
            self.cr.set_source_rgba(*self.rightcircle)
            self._circle(f.x, f.y, radius)
            self.cr.fill()

    def write(self):
        print "creating: ", self.outpng, 
        self.surf.write_to_png(self.outpng)
        print "\t done."

    def _createOutputFile(self):
        i = self.image.rfind('.')
        if i > 0:
            base = self.image[0:i]
            self.outpng = base +"_fix.png"
        else:
            self.outpng = self.image+"_fix.png"
        return self.outpng
        
def showOutput(eyedata, filename, smooth=False, compare=False, draw_saccades=False):
    '''
    Shows a matplot lib interactive gaze, the x and y components of
    an eye trial, the velocity wherein the eye moves.

    @param eyedata The eyedata to visualize
    @param filename the name of the eyefile
    @param smooth whether to show smoothed data
    '''
    eyeplot = EyeOutput(eyedata, filename, smooth, compare)

    # plot left eye
    if eyedata.hasLeftGaze():
        eyeplot._plotLGaze(smooth)
        if compare and not draw_saccades:
            eyeplot.compareLeft()
        if draw_saccades:
            eyeplot.plotLSaccades()
        else:
            eyeplot.plotLFixations()
    # plot right eye
    if eyedata.hasRightGaze():
        eyeplot._plotRGaze(smooth)
        if compare and not draw_saccades:
            eyeplot.compareRight()            
        if draw_saccades:
            eyeplot.plotRSaccades()
        else:
            eyeplot.plotRFixations()
    
    # plot gaze pattern over the stimulus
    if eyedata.hasLeftGaze() or eyedata.hasRightGaze():
        eyeplot._plotTrial()
        eyeplot.show()

def createFixPic(eyetrial):
    '''
    Creates a png image of the stimulus with the fixations
    inside the trial
    '''
    if _HAVE_CAIRO:
        im = FixationImage(eyetrial)
        im.write()
