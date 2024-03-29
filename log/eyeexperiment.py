#!/usr/bin/env python

"""
@package eyeexperiment
This file contains the implementation of Data contents of an eyetracker
experiment. It currently consists of an EyeExperiment, that contains
EyeTrials

@file eyeexperiment.py handles all eyeevents in an experiment
"""

from __future__ import annotations
from .eyelog import LogEntry
import re


class EyeTrial(object):
    """An EyeTrial contains all events in a single trials in a experiment

    In a log, all events are ordered in time. The eyetrial separates
    all events in logical event types. And optionally stores
    the presented stimulus.
    """

    def __init__(self):
        """initializes an empty trial"""
        ## The filename of the stimulus
        self.stimulus = None

        ## The entries of the left gaze samples
        self.lgaze = []
        ## The entries of the right gaze samples
        self.rgaze = []

        ## The left fixation entries as determined by iSpector
        self.lfix = []
        ## The right fixation entries as determined by iSpector
        self.rfix = []
        ## The average fixations entries as determined by iSpector
        self.avgfix = []

        ## the logged fixations by the eyetracker of the left eye
        self.loglfix = []
        ## the logged fixations by the eyetracker of the right eye
        self.logrfix = []
        ## the logged fixations by the eyetracker of the average eye signal
        self.logavgfix = []

        ## the saccades of the left eye determined by iSpector
        self.lsac = []
        ## the saccades of the right eye determined by iSpector
        self.rsac = []
        ## the saccades of the average eye determined by iSpector
        self.avgsac = []

        ## the logged saccades by the eyetracker of the left eye
        self.loglsac = []
        ## the logged saccades by the eyetracker of the right eye
        self.logrsac = []
        ## the logged saccades by the eyetracker of the averaged eye signal
        self.logavgsac = []

        ## the blinks of the left eye
        self.lblink = []
        ## the blinks of the right eye
        self.rblink = []

        ## the logged blinks of the left eye
        self.loglblink = []
        ## the logged blinks of the right eye
        self.logrblink = []

        ## meta trial information or samples that are precede the trial start
        self.meta = []

    def copy(self) -> EyeTrial:
        """Creates a deep copy of the EyeTrial"""
        cstim = str(self.stimulus)
        clgaze = [gaze.copy() for gaze in self.lgaze]
        crgaze = [gaze.copy() for gaze in self.rgaze]
        clfix = [fix.copy() for fix in self.lfix]
        crfix = [fix.copy() for fix in self.rfix]
        cavgfix = [fix.copy() for fix in self.avgfix]
        cloglfix = [fix.copy() for fix in self.loglfix]
        clogrfix = [fix.copy() for fix in self.logrfix]
        clogavgfix = [fix.copy() for fix in self.logavgfix]
        clsac = [sac.copy() for sac in self.lsac]
        crsac = [sac.copy() for sac in self.rsac]
        cavgsac = [sac.copy() for sac in self.avgsac]
        cloglsac = [sac.copy() for sac in self.loglsac]
        clogrsac = [sac.copy() for sac in self.logrsac]
        clogavgsac = [sac.copy() for sac in self.logavgsac]
        cmeta = [meta.copy() for meta in self.meta]

        clblink = [b.copy() for b in self.lblink]
        crblink = [b.copy() for b in self.rblink]
        cloglblink = [b.copy() for b in self.loglblink]
        clogrblink = [b.copy() for b in self.logrblink]

        newcopy = EyeTrial()
        newcopy.stimulus = cstim

        newcopy.lgaze, newcopy.rgaze = clgaze, crgaze

        newcopy.lfix, newcopy.rfix, newcopy.avgfix = clfix, crfix, cavgfix
        newcopy.loglfix, newcopy.logrfix, newcopy.logavgfix = (
            cloglfix,
            clogrfix,
            clogavgfix,
        )

        newcopy.lsac, newcopy.rsac, newcopy.avgsac = clsac, crsac, cavgsac
        newcopy.loglsac, newcopy.logrsac, newcopy.logavgsac = (
            cloglsac,
            clogrsac,
            clogavgsac,
        )

        newcopy.lblink = clblink
        newcopy.rblink = crblink
        newcopy.loglblink = cloglblink
        newcopy.logrblink = clogrblink

        newcopy.meta = cmeta

        return newcopy

    def __eq__(self, rhs):
        """instance equality

        @return True if two instances of EyeTrial are equal, false otherwise.
        """
        types = type(self) is type(rhs)

        if not types:
            return False
        else:
            return self.__dict__ == rhs.__dict__

    def __ne__(self, rhs):
        """
        Tests instance inequality
        @return True if two instances of EyeTrial are not equal, false otherwise.
        """
        return not (self == rhs)

    def addEntry(self, entry: LogEntry):
        """Add a LogEntry to this trial

        @param entry A LogEntry of type LGAZE, RGAZE, LFIX or RFIX
        """
        n = entry.getEntryType()

        if n == LogEntry.LGAZE:
            self.lgaze.append(entry)
        elif n == LogEntry.RGAZE:
            self.rgaze.append(entry)
        elif n == LogEntry.LFIX:
            self.loglfix.append(entry)
        elif n == LogEntry.RFIX:
            self.logrfix.append(entry)
        elif n == LogEntry.LSAC:
            self.loglsac.append(entry)
        elif n == LogEntry.RSAC:
            self.logrsac.append(entry)
        elif n == LogEntry.LBLINK:
            self.loglblink.append(entry)
        elif n == LogEntry.RBLINK:
            self.logrblink.append(entry)
        else:
            raise ValueError("Invalid type of logentry added to EyeTrial.")

    def addMeta(self, meta):
        """Add meta data to trial"""
        self.meta.append(meta)

    def setStimulus(self, name):
        """Set the stimulus for this file"""
        self.stimulus = name

    def containsGazeData(self):
        """Check whether this trial contains gaze samples"""

        return (len(self.lgaze) != 0) or (len(self.rgaze) != 0)

    def containsFixations(self):
        """Check whether this trial contains fixations"""

        return len(self.lfix) != 0 or len(self.rfix) != 0

    def containsLogFixations(self):
        """Check whether this trial contains fixations not determined by
        iSpector
        """

        return len(self.loglfix) > 0 or len(self.logrfix) > 0

    def containsLeftData(self):
        """Does this trial contain gaze sample of the left eye?"""

        return len(self.lgaze) > 0

    def containsRightData(self):
        """Does this trial contain gaze sample of the left eye?"""

        return len(self.rgaze) > 0

    def isMonocular(self):
        """Checks whether the data is this trial is monocular"""

        if len(self.lgaze) == 0 and len(self.rgaze) > 0:
            return True
        elif len(self.lgaze) > 0 and len(self.rgaze) == 0:
            return True
        else:
            return False

    def matchFixationsToSamples(self):
        """When you have monocular data it might be hard to guess
        whether the data is from the left or the right eye.
        this function maps right gaze to left fixations or vice versa.
        """

        if len(self.logrfix) and len(self.lgaze) and len(self.rgaze) == 0:
            self.rgaze = self.lgaze
            self.lgaze = []
        elif len(self.loglfix) and len(self.rgaze) and len(self.lgaze) == 0:
            self.lgaze = self.rgaze
            self.rgaze = []

    def fixFirstFix(self):
        """Sometimes the fixations are already started before the start
        of the trial. This method sets the first fixation identical
        to the first sample and adapts the duration.
        """
        refgaze = []

        if not self.lgaze and not self.rgaze:
            raise RuntimeError("Can't fix fixations without gazedata.")
        elif self.lgaze:
            refgaze = self.lgaze
        else:
            refgaze = self.rgaze

        if len(self.loglfix) > 0:
            if len(self.lgaze) == 0:
                self._fixFirstFixation(self.loglfix[0], refgaze[0])
            elif self.loglfix[0].getEyeTime() < self.lgaze[0].getEyeTime():
                self._fixFirstFixation(self.loglfix[0], self.lgaze[0])

        if len(self.logrfix) > 0:
            if len(self.rgaze) == 0:
                self._fixFirstFixation(self.logrfix[0], refgaze[0])
            elif self.logrfix[0].getEyeTime() < self.rgaze[0].getEyeTime():
                self._fixFirstFixation(self.logrfix[0], self.rgaze[0])

    def _fixFirstFixation(self, fix, sample):
        """fixes fix to match the sample."""
        fixstart = fix.getEyeTime()
        gazestart = sample.getEyeTime()
        diff = gazestart - fixstart

        if diff <= 0:
            return  # nothing to fix
        else:
            fix.eyetime += diff
            fix.duration -= diff

    def getEntries(self):
        """obtain a list of entries that belong to this trial

        @returns an unsorted list of entries inside this trial.
        """
        ret = []

        if self.lgaze:
            ret += self.lgaze

        if self.rgaze:
            ret += self.rgaze

        if self.lfix:
            ret += self.lfix

        if self.rfix:
            ret += self.rfix

        if self.avgfix:
            ret += self.avgfix

        if self.loglfix:
            ret += self.loglfix

        if self.logrfix:
            ret += self.logrfix

        if self.logavgfix:
            ret += self.logavgfix

        if self.lsac:
            ret += self.lsac

        if self.rsac:
            ret += self.rsac

        if self.avgsac:
            ret += self.avgsac

        if self.loglsac:
            ret += self.loglsac

        if self.logrsac:
            ret += self.logrsac

        if self.logavgsac:
            ret += self.logavgsac
        ret += self.meta

        return ret


class EyeExperiment(object):
    """EyeExperiment contains all the EyeTrials of one experiment.

    An EyeExperiment is a collection of EyeTrials and a bit of meta data
    of an experiment with eyetracking.
    """

    def _isTrialBegin(self, entry):
        """Determines if a LogEntry marks a trial begin

        @param entry a log.LogEntry
        """

        if entry.getEntryType() != LogEntry.MESSAGE:
            return False
        firstword = entry.message.split()[0]

        if firstword != "trialbeg":
            return False

        return True

    def _isTrialEnd(self, entry):
        """Determines if a LogEntry marks a trial begin

        @param entry a log.LogEntry
        """

        if entry.getEntryType() != LogEntry.MESSAGE:
            return False
        firstword = entry.message.split()[0]

        if firstword != "trialend":
            return False

        return True

    def _isPla(self, entry):
        """Determines if a LogEntry marks a stimulus

        @param entry a log.LogEntry
        """

        if entry.getEntryType() != LogEntry.MESSAGE:
            return False
        firstword = entry.message.split()[0]

        if firstword != "plafile":
            return False

        return True

    def _isSync(self, entry):
        """Determines if a LogEntry marks a stimulus

        @param entry a log.LogEntry
        """

        if entry.getEntryType() != LogEntry.MESSAGE:
            return False
        firstword = entry.message.split()[0]

        if firstword != "SYNCTIME":
            return False

        return True

    def _isTrialEntry(self, entry):
        """Determines if a Logentry should be added to a trial"""
        n = entry.getEntryType()

        if n in [
            LogEntry.RGAZE,
            LogEntry.LGAZE,
            LogEntry.RFIX,
            LogEntry.LFIX,
            LogEntry.RSAC,
            LogEntry.LSAC,
            LogEntry.LBLINK,
            LogEntry.RBLINK,
        ]:
            return True

        return False

    def __init__(self, entries):
        """Initializes an EyeExperiment by parsing a list of entries.


        @param entries a list of logentries from a logfile the entries
        should already be sorted on time.
        """
        ## All EyeTrials of an experiment
        self.trials = []

        ## messages written before a experiment is started.
        # Meta data of an experiment
        self.meta = []
        havestart = False
        foundsync = False
        trial = None
        tempmeta = []

        for i in entries:
            if trial and self._isTrialEntry(i) and foundsync:
                trial.addEntry(i)

                continue
            else:
                if not trial:
                    tempmeta.append(i)
                else:
                    for m in tempmeta:
                        trial.addMeta(m)
                    tempmeta = []
                    trial.addMeta(i)

            if not havestart:
                if self._isTrialBegin(i):
                    havestart = True
                else:
                    if i.getEntryType() == LogEntry.MESSAGE:
                        self.meta.append(i)

                    continue

            if self._isTrialBegin(i):
                trial = EyeTrial()

            if self._isTrialEnd(i):
                if trial is None:
                    raise RuntimeError("Encountered trialend without trialbeg")
                trial.addMeta(i)
                self.trials.append(trial)
                trial = None
                foundsync = False

                continue

            if self._isPla(i):
                if trial is None:
                    raise RuntimeError("Encountered pla without trialbeg")
                trial.setStimulus(i.message.split()[1])

            if self._isSync(i):
                foundsync = True

        for t in self.trials:
            # if t.isMonocular():
            #     t.matchFixationsToSamples()

            if t.containsLogFixations() and t.containsGazeData():
                t.fixFirstFix()

    def __eq__(self, rhs):
        """Examines whether to experiments hold equal data.

        @returns True if they are identical, but False when they are not.
        """
        types = type(self) is type(rhs)

        if not types:
            return False
        else:
            return self.__dict__ == rhs.__dict__

    def __ne__(self, rhs):
        """Examines whether two experiments hold different data.

        @returns True if the two experiments are different
        """

        return not (self == rhs)

    def getFixationName(self):
        """This function is for Fixation compatibility.

        It reads the meta data and extracts the
        useful parameters.
        Returns string with filename that is suitable for
        fixation tool (Cozijn 1996)

        @deprecated

        @return a string that Fixation likes as input filename
        """
        exp_name = ""
        subject_num = 0
        list_name = 0
        block_name = 0
        matchflags = re.I  # ignore case
        re_exp_name = re.compile(r"experiment:\s+(.*)", matchflags)
        re_subject_num = re.compile(r"participant:\s+[A-Za-z]*(\d.*)", matchflags)
        re_dummy_num = re.compile(r"participant:\s+dummy", matchflags)
        re_list_name = re.compile(r"list:\s+(.*)", matchflags)
        re_block_name = re.compile(r"recording:\s+(.*)", matchflags)

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

        retval = "{0:s}_{1:d}{2:d}_{3:03d}.asc".format(
            exp_name, list_name, block_name, subject_num
        )

        return retval

    def getEntries(self):
        """Returns a list of events in the trial.

        @returns a list of logentries of an experiment,
        the events are not sorted.
        """
        ret = []
        ret += self.meta

        for trial in self.trials:
            ret += trial.getEntries()

        return ret

    def copy(self):
        """Returns a deepcopy of self"""
        copytrials = [t.copy() for t in self.trials]
        copymeta = [m.copy() for m in self.meta]
        newexp = EyeExperiment([])
        newexp.trials = copytrials
        newexp.meta = copymeta

        return newexp
