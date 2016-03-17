
from eyelog import *
import re

class EyeTrial(object):
    
    def __init__(self):

        self.stimulus = None
        self.lgaze  = []
        self.rgaze  = []
        self.lfix   = []
        self.rfix   = []
        self.logfixl= []
        self.logfixr= []
        self.lsac   = []
        self.rsac   = []
        self.logsacl= []
        self.logsacr= []

    def addEntry(self, entry):
        n = entry.getEntryType()
        if n == LogEntry.LGAZE:
            self.lgaze.append(entry)
        elif n == LogEntry.RGAZE:
            self.rgaze.append(entry)
        elif n == LogEntry.LFIX:
            self.logfixl.append(entry)
        elif n == LogEntry.RFIX:
            self.logfixr.append(entry)
        else:
            raise ValueError("Invalid type of logentry added to EyeTrial.")
    
    def setStimulus(self, name):
        self.stimulus = name

    def containsGazeData(self):
        return (len(self.lgaze) != 0) or (len(self.rgaze) != 0)

    def containsFixations(self):
        return len(self.lfix) != 0 or len(self.rfix) != 0

    def containsLogFixations(self):
        return len(self.logfixl) > 0 or len(self.logfixr) > 0

    def containsLeftData(self):
        return len(self.lgaze) > 0

    def containsRightData(self):
        return len(self.rgaze) > 0

    def isMonocular(self):
        if len(self.lgaze) == 0 and len(self.rgaze) > 0:
            return True
        elif len(self.lgaze) > 0 and len(self.rgaze) == 0:
            return True
        else:
            return False

    def matchFixationsToSamples(self):
        ''' When you have monocular data it might be hard to guess
            whether the data is from the left or the right eye.
            this function maps right gaze to left fixations or vice versa.
        '''
        if len(self.logfixr) > 0 and len(self.lgaze) > 0 and len(self.rgaze) == 0:
            self.rgaze = self.lgaze
            self.lgaze = []
        elif len(self.logfixl) > 0 and len(self.rgaze) > 0 and len(self.lgaze) == 0:
            self.lgaze = self.rgaze
            self.rgaze = []

    def fixFirstFix(self):
        '''Sometimes the fixations are already started before the start
           of the trial. This method sets the first fixation identical
           to the first sample and adepts the duration.
        '''
        refgaze = []
        if (not self.lgaze and not self.rgaze) :
            raise RuntimeError("Can't fix fixations without gazedata.")
        elif self.lgaze:
            refgaze = self.lgaze
        else:
            refgaze = self.rgaze
        if len(self.logfixl) > 0:
            if len(self.lgaze) == 0:
                self._fixFistFixation(self.logfixl[0], refgaze[0])
            elif self.logfixl[0].getEyeTime() < self.lgaze[0].getEyeTime():
                self._fixFistFixation(self.logfixl[0], self.lgaze[0])

        if len(self.logfixr) > 0:
            if len(self.rgaze) == 0:
                self._fixFistFixation(self.logfixr[0], refgaze[0])
            elif self.logfixr[0].getEyeTime() < self.rgaze[0].getEyeTime():
                self._fixFistFixation(self.logfixr[0], self.rgaze[0])
    
    def _fixFistFixation(self, fix, sample):
        ''' fixes fix to match the sample. '''
        fixstart = fix.getEyeTime()
        gazestart = sample.getEyeTime()
        diff = gazestart - fixstart
        if diff <= 0:
            return # nothing to fix
        else:
            fix.eyetime += diff
            fix.duration -= diff


class EyeExperiment(object):

    def _isTrialBegin(self, entry):
        if entry.getEntryType() != LogEntry.MESSAGE:
            return False
        firstword = entry.message.split()[0]
        if firstword != "trialbeg":
            return False
        return True
        
    def _isTrialEnd(self, entry):
        if entry.getEntryType() != LogEntry.MESSAGE:
            return False
        firstword = entry.message.split()[0]
        if firstword != "trialend":
            return False
        return True

    def _isPla(self, entry):
        if entry.getEntryType() != LogEntry.MESSAGE:
            return False
        firstword = entry.message.split()[0]
        if firstword != "plafile":
            return False
        return True

    def _isSync(self, entry):
        if entry.getEntryType() != LogEntry.MESSAGE:
            return False
        firstword = entry.message.split()[0]
        if firstword != "SYNCTIME":
            return False
        return True

    def _isTrialEntry(self, entry):
        n = entry.getEntryType()
        if ( n == LogEntry.RGAZE or
             n == LogEntry.LGAZE or
             n == LogEntry.RFIX  or
             n == LogEntry.LFIX) :
            return True
        return False

    def __init__(self, entries):
        ''' 
            Init an experiment. This constructor reads the entries
            and builds it self based on those entries.

            @ entries a python list of LogEntries from module eyelog
        '''
        self.trials = []
        self.meta = []
        havestart = False
        foundsync = False
        trial = None
        for i in entries:
            if (havestart == False):
                if self._isTrialBegin(i):
                    havestart = True
                else:
                    if i.getEntryType() == LogEntry.MESSAGE:
                        self.meta.append(i)
            if self._isTrialBegin(i):
                trial = EyeTrial()
            if self._isTrialEnd(i):
                if trial == None:
                    raise RuntimeError("Encountered trialend without trialbeg")
                self.trials.append(trial)
                trial = None
                foundsync = False
            if self._isPla(i):
                if trial == None:
                    raise RuntimeError("Encountered pla without trialbeg")
                trial.setStimulus(i.message.split()[1])
            if self._isSync(i):
                #FIXME check how sync works exactly.
                foundsync = True
            if trial and self._isTrialEntry(i) and foundsync :
                trial.addEntry(i)

        for t in self.trials:
            #if t.isMonocular():
            #    t.matchFixationsToSamples()
            if t.containsLogFixations() and t.containsGazeData():
                t.fixFirstFix()

    def getFixationName(self):
        '''
        This function is for Fixation compability
        it reads the meta data and extracts the 
        usefull paramters.
        @return a value that Fixation likes as input filename
        '''
        exp_name    = ""
        subject_num = 0
        list_name   = 0 
        block_name  = 0
        matchflags = re.I # ingnore case
        re_exp_name     = re.compile(r'experiment:\s+(.*)',             matchflags)
        re_subject_num  = re.compile(r'participant:\s+[A-Za-z]*(\d.*)', matchflags)
        re_dummy_num    = re.compile(r'participant:\s+dummy',           matchflags)
        re_list_name    = re.compile(r'list:\s+(.*)',                   matchflags)
        re_block_name   = re.compile(r'recording:\s+(.*)',              matchflags)

        for i in self.meta:
            m = re_exp_name.match(i.message)
            if m:
                exp_name = m.group(1)
                exp_name = exp_name[:3]
            m = re_subject_num.match(i.message)
            if m:
                subject_num = int(m.group(1))
            m = re_dummy_num.match(i.message)
            if m:
                subject_num = 0
            m = re_list_name.match(i.message)
            if m:
                list_name = int(m.group(1))
            m = re_block_name.match(i.message)
            if m:
                block_name = int(m.group(1))

        retval = "{0:s}_{1:d}{2:d}_{3:03d}.asc".format(exp_name,
                                                       list_name,
                                                       block_name,
                                                       subject_num)
        return retval


        
