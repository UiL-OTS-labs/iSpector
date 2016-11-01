#!/usr/bin/env python

##
# \file eyedata.py
#
# EyeData contains the EyeData class which helps in detecting 
# fixations and saccades.
#
# \package log

import numpy as np
import matplotlib.pyplot as plt
from scipy.misc import imread
from scipy.stats import nanmean
from scipy.stats import nanmedian
import scipy as sp
from utils.tempsignal import savitzky_golay #newer version of scipy provide thereown version
from eyelog import *

##
# Generator to extract X coordinates
# @param gazeentrylist an iterable with gazeentries with only one type of logentries
# eg LGAZE or RGAZE
def generateXCoors(gazeentrylist):
    for i in gazeentrylist:
        yield i.x

##
# Generator to extract Y coordinates
# @param gazeentrylist an iterable with gazeentries with only one type of logentries
# eg LGAZE or RGAZE
def generateYCoors(gazeentrylist):
    for i in gazeentrylist:
        yield i.y


##
# Generator to extract the times of the gazeetries
# @param gazeentrylist an iterable with gazeentries with only one type of logentries
# eg LGAZE or RGAZE
def generateEyeTimes(gazeentrylist):
    for i in gazeentrylist:
        yield i.getEyeTime()

##
# Get a Numpy array with an eyesignal.
# @param gazeentrylist a list with gazeentries
#
def getValueArray(gazentrylist, generator):
    output = np.zeros(len(gazentrylist))
    for i, el in enumerate(generator(gazentrylist)):
        output[i] = el
    return output


class EyeData:
    '''
    \brief Finds fixations and saccades in eyemovement signals

    This class uses an eyetrial to obtain the eyetracking data of
    one trial and is able to plot that data and generate the results.
    '''

    ## Marks a start fixation 
    _sf = -1

    ## Marks an end fixation
    _ef = 1
    '''end fixation'''

    ##
    # Create a eyedata object that contains the signals for the left and righteye
    # when available in the eyetrial instance.
    #
    # @param method which method do use to find an indication of the noise.
    #       "mean" by taking the average of the signal "median" the median.
    # @param n set the threshold on n times the result of the outcome of method.
    # @param smooth whether or not smoothed signals should be used to determine
    #        the values of fixations
    # @param smoothwinsize the windowsize for the savitsky golay filter.
    # @param smoothorder the order of the polynomial to fit the signal within
    #        the window
    def __init__(self, method, n, smooth, smoothwinsize, smoothorder):
        #np.seterr('raise')
        ## boolean whether or not to smooth the data
        self.smooth     = smooth
        ## size of the smoothing window for the savitsky golay filter
        self.smoothwin  = smoothwinsize
        ## The polynomial order to which the signal is fitted while smoothing
        self.smoothorder= smoothorder
        ## The method is either mean or median and used to determine the velocity threshold.
        self.method     = method
        ## how many times the mean or median is taken to determine the final
        #  threshold value
        self.nmethod    = n
        ## The x signal for the left eye
        self.xgazeleft  = np.array([])
        ## The smoothed signal for the left eye
        self.xgazelefts = np.array([])
        ## The x coordinates for the right eye
        self.xgazeright = np.array([])
        ## The smoothed x coordinates for the right eye
        self.xgazerights= np.array([])
        ## The y signal for the left eye
        self.ygazeleft  = np.array([])
        ## The smoothed y signal for the left y
        self.ygazelefts = np.array([])
        ## the y signal for the right eye
        self.ygazeright = np.array([])
        ## the smoothed y signal for the left eye.
        self.ygazerights= np.array([])
        ## The velocity of the left eye
        self.velol      = np.array([])
        ## The velocity of the right eye
        self.velor      = np.array([])
        ## The smoothed velocity of the left eye
        self.velols     = np.array([])
        ## The smoothed velocity of the right eye
        self.velors     = np.array([])
        ## Helper array to find fixations of the left eye
        self.fixl       = np.array([])
        ## Helper array to find fixations of the right eye
        self.fixr       = np.array([])
        ## Helper array to find saccades of the left eye
        self.sacl       = np.array([])
        ## Helper array to find saccades of the right eye
        self.sacr       = np.array([])
        ## list of fixation of the left eye
        self.lfixlist   = []
        ## list of fixation of the right eye
        self.rfixlist   = []
        ## list of saccades of the left eye
        self.lsaclist   = []
        ## list of saccades of the right eye
        self.rsaclist   = []

    ## ProcessTrial determines fixations and saccades in one trial
    # 
    # ProcessTrials determines how fast an eye is moving. If the eye is moving
    # a a speed below the threshold we conclude the eye fixating. In contrast
    # if the speed is above the threshold we say the eye is saccading.
    # In theory the eye could be in smoothpursuit mode, and EyeData would
    # consider it a fixation or saccade falsely.
    #
    # @param eyetrial and EyeTrial instance
    # @param overwritefix
    # \todo implement parameter overwritefix there should be more trials parameters
    # available. Perhaps it is better to contain trial/experiment meta data here.
    # this class should be dedicated to eyemovement only.
    def processTrial(self, eyetrial, overwritefix=False):
        ## The stimulus for this file
        self.stimfile   = eyetrial.stimulus
        self.xgazeleft  = getValueArray(eyetrial.lgaze, generateXCoors)
        self.ygazeleft  = getValueArray(eyetrial.lgaze, generateYCoors)
        self.xgazeright = getValueArray(eyetrial.rgaze, generateXCoors)
        self.ygazeright = getValueArray(eyetrial.rgaze, generateYCoors)
        ## The logged fixations of the left eye
        self.loglfix    = eyetrial.loglfix
        ## The logged fixations of the right eye
        self.logrfix    = eyetrial.logrfix

        ## the median velocity of the left eye
        self.medvelol   = 0 
        ## the median velocity of the right eye
        self.medvelor   = 0

        ## vector of eyetimes of the left gaze
        self.lgazetimes = getValueArray(eyetrial.lgaze, generateEyeTimes)
        ## vector of eyetimes of the right gaze
        self.rgazetimes = getValueArray(eyetrial.rgaze, generateEyeTimes)
        
        if self.hasLeftGaze():
            ## approximation of the duration of a sample of the left eye
            self.lsampletime = sp.median(sp.diff(self.lgazetimes))
        if self.hasRightGaze():
            ## approximation of the duration of a sample of the right eye
            self.rsampletime = sp.median(sp.diff(self.rgazetimes))

        # values with 0.0 as value should not be considered as data
        self.xgazeleft  [self.xgazeleft  == 0] = float('nan')
        self.ygazeleft  [self.ygazeleft  == 0] = float('nan')
        self.xgazeright [self.xgazeright == 0] = float('nan')
        self.ygazeright [self.ygazeright == 0] = float('nan')
        
        #obtain smoothed signals
        if self.smooth == True:
            if self.hasRightGaze():
                if len(self.ygazeright) > self.smoothwin:
                    self.ygazerights = savitzky_golay(self.ygazeright, self.smoothwin, self.smoothorder)
                else:
                    self.ygazerights = self.ygazeright

                if len(self.xgazeright) > self.smoothwin:
                    self.xgazerights = savitzky_golay(self.xgazeright, self.smoothwin, self.smoothorder)
                else:
                    self.xgazerights = self.xgazeright

            if self.hasLeftGaze():
                if len(self.xgazeleft) > self.smoothwin:
                    self.xgazelefts  = savitzky_golay(self.xgazeleft, self.smoothwin, self.smoothorder)
                else:
                    self.xgazelefts = self.xgazeleft

                if len(self.ygazeleft) > self.smoothwin:
                    self.ygazelefts  = savitzky_golay(self.ygazeleft, self.smoothwin, self.smoothorder)
                else:
                    self.ygazelefts = self.ygazeleft
                

        # compute differential signals

        ## the differntial signal of the left x signal
        self.ldiffx = np.diff(self.xgazeleft)
        ## the differntial signal of the left y signal
        self.ldiffy = np.diff(self.ygazeleft)
        ## the differntial signal of the right x signal
        self.rdiffx = np.diff(self.xgazeright)
        ## the differntial signal of the right y signal
        self.rdiffy = np.diff(self.ygazeright)
        
        if self.smooth == True:
            if self.hasLeftGaze():
                ## smoothed version of self.ldiffx 
                self.ldiffxs = np.diff(self.xgazelefts)
                ## smoothed version of self.ldiffy 
                self.ldiffys = np.diff(self.ygazelefts)
            if self.hasRightGaze():
                ## smoothed version of self.diffx 
                self.rdiffxs = np.diff(self.xgazerights)
                ## smoothed version of self.rdiffy 
                self.rdiffys = np.diff(self.ygazerights)
        else:
            if self.hasLeftGaze():
                ## smoothed version of self.ldiffx 
                self.ldiffxs = self.ldiffx 
                ## smoothed version of self.ldiffy 
                self.ldiffys = self.ldiffy
            if self.hasRightGaze():
                ## smoothed version of self.rdiffx 
                self.rdiffxs = self.rdiffx
                ## smoothed version of self.rdiffy 
                self.rdiffys = self.rdiffy

        # compute velocities
        if self.hasLeftGaze():
            self.velol   = np.sqrt(self.ldiffy*self.ldiffy + self.ldiffx*self.ldiffx)
            self.velol   = self.velol / self.lsampletime
        else:
            self.velol = np.array([])
        if self.hasRightGaze():
            self.velor   = np.sqrt(self.rdiffy*self.rdiffy + self.rdiffx*self.rdiffx)
            self.velor   = self.velor / self.rsampletime
        else:
            self.velor = np.array([])
        
        if len(self.velol) > 0:
            self.medvelol= nanmedian(self.velol)
        else:
            self.medvelol = float('nan')
        if (len(self.velor) > 0):
            self.medvelor= nanmedian(self.velor)
        else:
            self.medvelor = float('nan')

        if len(self.velol) > 0:
            try :
                ## the mean velocity of the left eye signal
                self.meanvelol=nanmean(self.velol)
            except FloatingPointError as e:
                print self.velol
                exit(e)
        else:
            self.meanvelol=float('nan')
        
        if len(self.velor) > 0:
            try:
                ## the mean velocity of the right eye signal
                self.meanvelor=nanmean(self.velor)
            except FloatingPointError as e:
                print self.velor
                exit(e)
        else:
            self.meanvelor=float('nan')

        if self.smooth == True:
            # these outcommented smoothing procedures would smooth the velocity
            # I feel that a combined smoothed velocity signal from the smooted
            # x and y signal is better. I'm not so sure actually.
            if self.hasLeftGaze():
                self.velols = savitzky_golay(self.velol, self.smoothwin, self.smoothorder)
            if self.hasRightGaze():
                self.velors = savitzky_golay(self.velor, self.smoothwin, self.smoothorder)
#            if (self.hasLeftGaze()):
#                self.velols = np.sqrt(self.ldiffys*self.ldiffys + self.ldiffxs*self.ldiffxs)
#                self.velols = self.velols / self.lsampletime
#            if (self.hasRightGaze()):
#                self.velors = np.sqrt(self.rdiffys*self.rdiffys + self.rdiffxs*self.rdiffxs)
#                self.velors = self.velors / self.rsampletime

        self._determineThreshold(self.method, self.nmethod)

        self._findFixations()
        self._findSaccades()

        self._correctFixationsByDuration()

#        if len(eyetrial.lfix) == 0 or overwritefix and self.hasLeftGaze():
#            self._etAttachLFix(eyetrial)
#        if len(eyetrial.rfix) == 0 or overwritefix and self.hasRightGaze():
#            self._etAttachRFix(eyetrial)
#        if len(eyetrial.lsac) == 0 or overwritesac and self.hasLeftGaze():
#            #self._etAttachLSac()
#            pass #TODO
#        if len(eyetrial.rsac) == 0 or overwritesac and self.hasRightGaze():
#            #self._etAttachRSac()
#            pass #TODO

    ##
    # sets the final threshold
    #
    # Determines the velocity threshold. A velocity below this threshold means
    # at this point in the signal the eye is fixating, otherwise the eye
    # is considered to be making a saccade.
    #
    # @param method find the base noise level based on the median or mean
    # of the signal, the valid values are "mean" and "median"
    # @param ntimes A float that tell many times we take the mean or median
    # to determine the final value for the threshold.
    #
    def _determineThreshold(self, method="mean", ntimes=1.0):
        valid = ["mean", "median", "snr"]
        if not method in valid:
            raise ValueError("Method must be one of " + str(valid))

        if method == "mean":
            ## a tuple of thresholds of the left and right signal respectively
            self.threshold = self.meanvelol * ntimes, self.meanvelor * ntimes
        elif method == "snr":
            nan = float('nan')
            if self.hasLeftGaze():
                leftsnr = self.meanvelol / np.std(self.velol[np.isfinite(self.velol)]) \
                            * ntimes
            else:
                leftsnr = nan
            if self.hasRightGaze():
                rightsnr = self.meanvelor / np.std(self.velor[np.isfinite(self.velor)]) \
                        * ntimes
            else:
                rightsnr = nan
            if self.hasRightGaze():
                if not (rightsnr > 0):
                    print self.velor, rightsnr, self.meanvelor
                    raise ValueError('We have gazedata but are unable to calculate a snr')
            if self.hasLeftGaze():
                if not (leftsnr > 0):
                    print self.velol, leftsnr, self.meanvelol
                    raise ValueError('We have gazedata but are unable to calculate a snr')
            self.threshold = leftsnr, rightsnr
        else:
            self.threshold = self.medvelol * ntimes, self.medvelor * ntimes

    ##
    # This function tries to correct Fixations that are unreasonably short.
    #
    # This function examines fixations by duration
    # it tries to remove fixations shorther than a
    # certain duration. It tries to merge fixations if two
    # are very close together and removes saccades in between.
    # Otherwise if they are not close together, the fixation is removed
    # and the two (if two) saccades are merged.
    #
    def _fixFixSac(self, fixvec, sacvec, timevec, xgaze, ygaze, entrytype, duration = 50) :
        #TODO merge nearby fixations
        if (len(fixvec) != len(sacvec) or len(sacvec) != len(timevec) or len(timevec) == 0):
            raise ValueError("empty input or the length of the input is not equal")
        # fist we will get an approximation of the fixations and saccades.
        fixations = self._getFixList(timevec, fixvec, xgaze, ygaze, entrytype)
        # Select all fixations longer than duration.
        longlist = [fix for fix in fixations if fix.duration >= duration]
        fixvec *= 0
        for fix in longlist:
            fixvec[timevec == fix.getEyeTime()] = self._sf
            fixvec[timevec == (fix.getEyeTime() + fix.duration)] = self._ef
        fixations = self._getFixList(timevec, fixvec, xgaze, ygaze, entrytype)
        sacvec *= 0
        et = None

        if entrytype == LogEntry.RFIX:
            et = LogEntry.RSAC
        elif entrytype == LogEntry.LFIX:
            et = LogEntry.LSAC
        else:
            raise Valuerror("entry type should be LogEntry.LFIX or LogEntry.RFIX")

        # loop over fixations if in between fixations are nans don't consider
        # it to be a saccade
        saccades = []
        for i in range(1, len(fixations)):
            startfix = fixations[i-1]
            endfix   = fixations[i]
            start    = startfix.getEyeTime() + startfix.duration
            end      = endfix.getEyeTime()
            #correct the timestamps with one sample (this is what EyeLink does, but it is ugly)
            start    = timevec[np.where(timevec==start)[0] + 1][0]
            end      = timevec[np.where(timevec==end)[0] - 1][0]
            if np.isnan(np.sum(xgaze[np.logical_and(timevec > start, timevec < end)] )):
                # in the time between two fixations are nan(s)
                continue
            duration = end - start
            saccades.append(
                    SaccadeEntry(et, start, duration, startfix.x,
                                 startfix.y, endfix.x, endfix.y)
                    )
        sacvec *= 0
        for sac in saccades:
            sacvec[timevec == sac.getEyeTime()] = EyeData._sf
            sacvec[timevec == (sac.getEyeTime() + sac.duration)] = EyeData._ef
        return fixations, saccades

    def _correctFixationsByDuration(self, ms=50.0):
        ''' This function corrects fixations,
            if fixations are shorter than ms.
            It also creates saccades on basis
            of those fixations
        '''
        if self.hasLeftGaze():
            self.lfixlist, self.lsaclist = self._fixFixSac(
                                self.fixl,
                                self.sacl,
                                self.lgazetimes,
                                self.xgazeleft,
                                self.ygazeleft,
                                LogEntry.LFIX,
                                ms
                                )
        if self.hasRightGaze():
            self.rfixlist, self.rsaclist = self._fixFixSac(self.fixr,
                            self.sacr,
                            self.rgazetimes,
                            self.xgazeright,
                            self.ygazeright,
                            LogEntry.RFIX,
                            ms
                            )
    
    def _findFixations(self):
        ''' 
        Uses the velocities to determine the fixations
        '''
        lthreshold = None
        rthreshold = None
        if self.smooth == True:
            if self.hasLeftGaze():
                lthreshold = self.velols
            if self.hasRightGaze():
                rthreshold = self.velors
        else:
            if self.hasLeftGaze():
                lthreshold = self.velol
            if self.hasRightGaze():
                rthreshold = self.velor

        if self.hasLeftGaze():
            self.fixl = np.concatenate( [[0], lthreshold < self.threshold[0]])
            fixl2 = np.concatenate( [lthreshold < self.threshold[0], [0]])
            self.fixl = self.fixl - fixl2

        if self.hasRightGaze():
            self.fixr = np.concatenate( [[0], rthreshold < self.threshold[1]])
            fixr2 = np.concatenate( [rthreshold < self.threshold[1], [0]])
            self.fixr = self.fixr - fixr2
    
    def _findSaccades(self):
        ''' 
        Uses the velocities to determine the saccades
        '''
        lthreshold = None
        rthreshold = None
        if self.smooth == True:
            lthreshold = self.velols
            rthreshold = self.velors
        else:
            lthreshold = self.velol
            rthreshold = self.velor

        self.sacl = np.concatenate( [[0], lthreshold > self.threshold[0]])
        sacl2 = np.concatenate( [lthreshold > self.threshold[0], [0]])
        self.sacl = self.sacl - sacl2
        
        self.sacr = np.concatenate( [[0], rthreshold > self.threshold[1]])
        sacr2 = np.concatenate( [rthreshold > self.threshold[1], [0]])
        self.sacr = self.sacr - sacr2

#TODO rewrite this functions as one and adapt the time of the first fixation to match the first gaze data
    def _etAttachRFix(self, et):
        '''
        attaches the right fixations to et.
        Note this clears the existing fixations.
        '''
        et.rfix = self._getFixList(self.rgazetimes, self.fixr, self.xgazeright, self.ygazeright, LogEntry.RFIX)
    
    def _etAttachLFix(self, et):
        '''
        attaches the left fixations to et.
        Note this clears the existing fixations.
        '''
        et.lfix = self._getFixList(self.lgazetimes, self.fixl, self.xgazeleft, self.ygazeleft, LogEntry.LFIX)

    ##
    # Get a list of fixations
    def _getFixList(self, gazetimes, startendfix, xgaze, ygaze, entrytype):
        fixations = []
        if entrytype != LogEntry.LFIX and entrytype != LogEntry.RFIX :
            raise ValueError("entrytype != LogEntry.LFIX and entrytype != LogEntry.RFIX")
        if len(gazetimes) <= 0:
            return fixations
        starttimes = gazetimes [startendfix == self._sf]
        endtimes = gazetimes [startendfix == self._ef] 
        if len(starttimes) != len(endtimes):
            raise ValueError("There is no end time for every starttime or vice versa.")
        for i in range(len(starttimes)):
            start = starttimes[i]
            end = endtimes[i]
            duration = end - start
            boolvec = np.logical_and(gazetimes >= start, gazetimes <= end)
            if (duration < 0):
                raiseValueError("Endtime before start time")
            meanx = sp.mean(xgaze[boolvec])
            meany = sp.mean(ygaze[boolvec])
            fixations.append(
                FixationEntry(entrytype, start, duration, meanx, meany)
                )
        return fixations

    ## Get the eyemovement raw signal of the left eye
    # @param smoothed returns the smoothed signals
    # 
    # \return a tuple of the x and y signal as numpy arrays of the left eye.
    def getLeft(self, smoothed=False):
        if smoothed == True:
            return self.xgazelefts, self.ygazelefts
        else:
            return self.xgazeleft, self.ygazeleft
    
    ##
    # Returns the velocity of the left eye
    def getLeftVelocity(self, smoothed=False):
        if smoothed == True:
            return self.velols
        else:
            return self.velol

    ## Get the eyemovement raw signal of the right eye
    # @param smoothed returns the smoothed signals
    # 
    # \return a tuple of the x and y signal as numpy arrays of the right eye.
    def getRight(self, smoothed=False):
        '''
        Returns the signals of x and y as numpy arrays.
        @param smoothed return the smoothed signals

        @returns tuple of x and y signal respectively
        '''
        if smoothed==True:
            return self.xgazerights, self.ygazerights
        else:
            return self.xgazeright, self.ygazeright
    
    ##
    # Returns the velocity of the right eye
    def getRightVelocity(self, smoothed=False):
        if smoothed == True:
            return self.velors
        else:
            return self.velor

    ## Check whether the EyeData contains sample of the left eye
    def hasLeftGaze(self):
        return len (self.xgazeleft) > 0

    ## Check whether the EyeData contains sample of the right eye
    def hasRightGaze(self):
        return len (self.xgazeright) > 0

    ## return a tuple of times belonging to the right and left eye respectively
    def getTimes(self):
        return self.lgazetimes, self.rgazetimes
    
    ## 
    # returns a tuple of vectors the first items contains a vector of leftfixations
    # the second returns a vector with the right fixations. a -1 means a fixation
    # starts and a 1 means a fixation ends
    def getFixVecs(self):
        return self.fixl, self.fixr
    
    ##
    # returns a tuple of vectors, the first item contains a vector of  of the left
    # saccade and the second returns the right saccades. a -1 means a saccade start
    # and a 1 means fixation start.
    def getSacVecs(self):
        return self.sacl, self.sacr

    ##
    #Returns the found fixations
    def getFixations(self):
        return self.lfixlist, self.rfixlist
    
    ##
    #Return saccades in list
    def getSaccades(self):
        return self.lsaclist , self.rsaclist

    ##
    # returns the velocity vectors of the left and right eye
    def getVelo(self, smooth=False):
        if (smooth):
            return self.velols, self.velors
        else:
            return self.velol, self.velor

    ##
    # returns a tuple with the median velocity of the left and right eye
    # respectively
    def getMedVelo(self):
        return self.medvelol, self.medvelor

    ##
    # returns a tuple with the mean velocity of the left and right eye
    def getMeanVelo(self):
        return self.meanvelol, self.meanvelor

    ##
    # returns a value of the threshold
    def getThreshold(self):
        return self.threshold

