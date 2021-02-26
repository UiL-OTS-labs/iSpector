#!usr/bin/env python
'''Eyelog.py is a module that contains of all classes needed to
create an logfile for the analysis of behavioral experiments
that yield eyemovement data.
In theory an experiment consists of a series of trials.
In a trial are a number of events that can occur. Events
are the occurence of samples of the eyetracker, fixations, saccades
etc. An event is characterized by a timestamp and a type.
Events will be primaraly sorted on timestamp and then on the type.
'''

##
# \file eyelog.py
# This file contains utilities for log files.
#

import itertools
import functools
import abc 

##
#An abstract base class for all LogEntries in an eyelog.
class LogEntry (abc.ABC):

    ## LogEntry contains functions from a ABCMeta classes
    LGAZE       = 0
    ## Entry that describes a right gaze sample
    RGAZE       = 1
    ## Entry that describes a left fixation
    LFIX        = 2
    ## Entry that describes a right fixation
    RFIX        = 3
    ## Entry that describes a stimulus
    STIMULUS    = 4
    ## Entry that describes a user defined message
    MESSAGE     = 5
    ## Entry that describes a saccade of the left eye
    LSAC        = 6
    ## Entry that descibes a saccade of the right eye
    RSAC        = 7

    # extended types these don't belong to a log, but can be handy for unhandy formats
    # that log a end event, or do some other marking like Begin and end

    ## Is a gaze in a eyelink asc log
    ASCGAZE = 8
    ## Is a Eyelink fixation end in a asc log of the left eye
    FIXENDL = 9
    ## Is a Eyelink fixation end in a asc log of the right eye
    FIXENDR = 10
    ## Is a saccade end in an asc log of the left eye.
    SACCENDL= 11
    ## Is a saccade end in an asc log of the right eye.
    SACCENDR= 12
    ## Mark a begin in a ascii log
    BEGIN   = 13
    ## Mark an end in a ascii log
    END     = 14

    ## The separator used to separate columns.
    SEP     = '\t'

    ## Construct an instance of LogEntry
    #
    # @param entrytype defines what kind of log entry this is.
    # @param eyetime A float that marks the time in the time of the eyetracker.
    def __init__(self, entrytype, eyetime):
        ## The type of entry of this LogEntry
        self.entrytype  = entrytype
        self.eyetime    = eyetime

    ## Tell what kind of LogEntry this is.
    def getEntryType(self) :
        return self.entrytype

    ## Compares for object equality
    def __eq__(self, other):
        return type(self) is type(other) and self.__dict__ == other.__dict__

    ## Compares for object difference
    def __ne__(self, other):
        return not self == other

    ## This marks the timepoint in milliseconds when
    def getEyeTime(self):
        return self.eyetime

    ## callback used to sort logentries on time
    @staticmethod
    def sortCallback(el, er):
        diff = el.getEyeTime() - er.getEyeTime()
        if diff < 0:
            return -1
        elif diff == 0:
            return 0
        else:
            return 1

    ## Serialize this logentry in EyeLink Ascii format
    #
    # @return A string that descibes the event suitable for a eyelink log.
    @abc.abstractmethod
    def toAsc(self):
        ''' Implement return of string in format as Eyelink edf to ascii does. '''
        pass

    ##
    # Create a deep copy of this instance
    #
    @abc.abstractmethod
    def copy(self):
        pass

#    @abstractmethod
#    def __str__():
#        ''' Implement return of string in format as Eyelink edf to ascii does. '''
#        pass

    ## Returns True if this is a left gaze sample
    @staticmethod
    def isLGaze(entry):
        return entry.getEntryType() == LogEntry.LGAZE

    ## Returns True if this is a right gaze sample
    @staticmethod
    def isRGaze(entry):
        return entry.getEntryType() == LogEntry.RGAZE

    ## Returns True if this is a gaze sample
    @staticmethod
    def isGaze(entry):
        return LogEntry.isLGaze(entry) or LogEntry.isRGaze(entry)

    ## Returns True if this is a fixation
    @staticmethod
    def isFixation(entry):
        ''' Determines whether a LogEntry is a fixaton '''
        return entry.getEntryType() == LogEntry.LFIX or entry.getEntryType() == LogEntry.RFIX

    ## Returns True if this is a saccade
    @staticmethod
    def isSaccade(entry):
        ''' Determines whether a LogEntry is a saccade '''
        return entry.getEntryType() == LogEntry.LSAC or entry.getEntryType() == LogEntry.RSAC

    ## Returns True if this is a message entry
    @staticmethod
    def isMessage(entry):
        return entry.getEntryType() == LogEntry.MESSAGE

    ## Function usefull for removing fixations and or saccades from the log.
    @staticmethod
    def _removeEyeEvents(entry):
        return not (LogEntry.isFixation(entry) or LogEntry.isSaccade(entry))

    ##
    # Removes all fixations and saccades from the log.
    #
    # \param entries a list (iterable) of LogEntry
    # \returns list of filtered entries.
    @staticmethod
    def removeEyeEvents(entries):
        entries = filter(LogEntry._removeEyeEvents, entries)
        return list(entries)

    ## Removes the left gaze entries.
    #
    # can be used to obtain a list without the left gaze
    # \param entries a list (iterable) of LogEntry
    @staticmethod
    def removeLeftGaze(entries):
        filt = lambda e: not e.getEntryType() == LogEntry.LGAZE
        return list(filter(filt, entries))

    ##
    # Removes the right gaze entries
    #
    # can be used to obtain a list without the right gaze '''
    # \param entries an iterable
    @staticmethod
    def removeRightGaze(entries):
        filt = lambda e: not e.getEntryType() == LogEntry.RGAZE
        return list(filter(filt, entries))


##
#This describes a left or right eye gaze sample of the eyetracker.
class GazeEntry(LogEntry) :

    ##
    # construct a GazeEntry
    #
    # \param entrytype LogEntry.RGAZE or LogEntry.LGaze
    # \param eyetime the time on the eyetracker when the gaze was sampled
    # \param x float of the x-coordinate of the gaze
    # \param y float of the y-coordinate of the gaze
    # \param pupil the pupilsize during the gazesample
    def __init__(self, entrytype, eyetime, x, y, pupil) :
        super(GazeEntry, self).__init__(entrytype, eyetime)
        ## the x coordinate of the gaze sample
        self.x = x
        ## the y coordinate of the gaze sample
        self.y = y
        ## the pupilsize of the gaze sample
        self.pupil = pupil

    ## 
    # Create a copy from the original
    #
    def copy(self):
        return GazeEntry(self.entrytype, self.eyetime, self.x, self.y, self.pupil)

    ##
    # Create a string from self in Eyelink ascii format
    def toAsc(self):
        raise ValueError("GazeEntries should not be converted to .asc format")

##
#An entry in a logfile that logs the gaze compatible for Fixation program(Cozijn)
class AscGazeEntry(LogEntry):

    ##
    # \param lgaze a GazeEntry for the left eye
    # \param rgaze a GazeEntry for the right eye
    def __init__(self, lgaze, rgaze):
        time = None
        if lgaze:
            time = lgaze.getEyeTime()
        elif rgaze:
            time = rgaze.getEyeTime()
        else:
            raise ValueError("Both lgaze and rgaze are not valid")

        super(AscGazeEntry, self).__init__(LogEntry.ASCGAZE, time)

        ## contains a GazeEntry for the left eye.
        self.lgaze = lgaze
        ## contains a GazeEntry for the right eye.
        self.rgaze = rgaze

    ##
    # deep copy the asc gaze entry
    def copy(self):
        return AscGazeEntry(self.lgaze, self.rgaze)
    ##
    # Create a string from self in Eyelink ascii format
    def toAsc(self):
        string = str(int(self.getEyeTime()))
        SEP = LogEntry.SEP
        #TODO check if fixation performs better if times are in integers
        if self.lgaze:
            string += (SEP + str(self.lgaze.x) + SEP + str(self.lgaze.y) + SEP
                           + str(self.lgaze.pupil)
                           )
        if self.rgaze:
            string += (SEP + str(self.rgaze.x) + SEP + str(self.rgaze.y) + SEP
                           + str(self.rgaze.pupil)
                           )
        return string

##
# A FixationEntry Describes a fixation of the left or right eye
#
# A fixation is determined by a location on a 2D plane and ,its time
# and the duration of the fixation.
class FixationEntry(LogEntry):

    ##
    # Init a fixation entry
    #
    # \param entrytype  Must be LogEntry.LFIX or LogEntry.RFIX
    # \param eyetime    The time (ms) on the eyetracker when the fixation starts.
    # \param eyedur     The duration of the fixation.
    # \param x          The x coordinate of the fixation
    # \param y          The y coordinate of the fixation
    def __init__(self, entrytype, eyetime, eyedur, x, y):
        super(FixationEntry,self).__init__(entrytype, eyetime)
        self.x = x
        ## the y coordinate of this fixation
        self.y = y
        ## the duration of this fixation
        self.duration = eyedur

    def copy(self):
        return FixationEntry(
            self.entrytype, self.eyetime, self.duration, self.x, self.y
        )

    ##
    # Create a string from self in Eyelink ascii format
    def toAsc(self):
        ssac = ""
        if self.getEntryType() == LogEntry.LFIX:
            ssac = "SFIX\tL\t"
        else:
            ssac = "SFIX\tR\t"
        return ssac + str(int(self.getEyeTime()))

## This class can be used to mark fixation ends in an asc log.
class FixationEndEntry(LogEntry):

    ##
    # @param fixation a valid FixationEntry
    def __init__(self, fixation):
        ## The FixationEntry that belongs to this end entry.
        self.fixation = fixation
        time = fixation.getEyeTime() + fixation.duration
        entry = None
        if fixation.getEntryType() == LogEntry.LFIX:
            entry = LogEntry.FIXENDL
        elif fixation.getEntryType() == LogEntry.RFIX:
            entry = LogEntry.FIXENDR
        else:
            raise ValueError("Fixation entry should be initialized with LFIX or RFIX")
        super(FixationEndEntry, self).__init__(entry, time)
    
    ##
    # create a deepcopy of oneself
    def copy(self):
        return FixationEntry(self.fixation)

    ##
    # Create a string from self in Eyelink ascii format
    def toAsc(self):
        efix = ""
        if self.getEntryType() == LogEntry.FIXENDL:
            efix = "EFIX\tL"
        elif self.getEntryType() == LogEntry.FIXENDR:
            efix = "EFIX\tR"
        else: raise ValueError("Wrong entry type in FixationEndEntry")

        SEP = LogEntry.SEP
        return efix + SEP + str(int(self.fixation.getEyeTime()))+  \
                      SEP + str(int(self.getEyeTime()))         +  \
                      SEP + str(int(self.fixation.duration))    +  \
                      SEP + str(self.fixation.x)                +  \
                      SEP + str(self.fixation.y)                +  \
                      SEP + str(int(self.fixation.duration))

## A logged user defined message in a string.
#
class MessageEntry(LogEntry):

    ##
    # \param eyetime the time of the message in eyetracking time
    # \param message a used defined string
    def __init__(self, eyetime, message):
        super(MessageEntry, self).__init__(LogEntry.MESSAGE, eyetime)
        ## the message of this Message entry
        self.message = message
    
    ##
    # Return a deepcopy of the message entry
    def copy(self):
        return MessageEntry(self.eyetime, str(self.message))

    ##
    # Create a string from self in Eyelink ascii format
    def toAsc(self):
        return "MSG" + "\t" + str(int(self.getEyeTime())) + "\t" + self.message

##
# SaccadeEntry This describes a saccade in an experiment
#
# A saccade is defined by its eye, a starttime, duration and start and end position
class SaccadeEntry(LogEntry):

    ##
    # Initialize a SaccadeEntry
    #
    # \param et must be LogEntry.LSAC or LogEntry.ESAC
    # \param eyetime the time (ms) on eyetracker when the saccade started
    # \param duration the duration(ms) of the saccade
    # \param xstart starting x coordinate.
    # \param ystart starting y coordinate.
    # \param xend end x coordinate.
    # \param yend end y coordinate.
    def __init__(self,
                 et,
                 eyetime,
                 duration,
                 xstart,
                 ystart,
                 xend,
                 yend
                 ):
        super(SaccadeEntry, self).__init__(et, eyetime)
        ## x coordinate of the start
        self.xstart = xstart
        ## y coordinate of the start
        self.ystart = ystart
        ## x coordinate of the end position
        self.xend   = xend
        ## y coordinate of the end position
        self.yend   = yend
        ## duration of the saccade in ms.
        self.duration = duration
    
    ##
    # create a deep copy of oneself
    def copy(self):
        return SaccadeEntry(
            self.entrytype, self.eyetime, self.duration,
            self.xstart, self.ystart, self.xend, self.yend
        )

    ##
    # Create a string from self in Eyelink ascii format
    def toAsc(self):
        string =""
        SEP = LogEntry.SEP
        if self.getEntryType() == LogEntry.RSAC:
            string += ("SSACC" + SEP + "R" + SEP + str(int(self.getEyeTime())) )
        elif self.getEntryType() == LogEntry.LSAC:
            string += ("SSACC" + SEP + "L" + SEP + str(int(self.getEyeTime())) )
        else: raise ValueError("Unknown entry type")
        return string

## A marker for saccade end in a Eyelink ascii log.
class SaccadeEndEntry(LogEntry):

    ##
    # inits a SaccadeEndEntry
    def __init__(self, saccade):
        ## the saccade that belong to this end marker
        self.saccade = saccade
        start = saccade.getEyeTime() + saccade.duration
        entry = None
        if saccade.getEntryType() == LogEntry.RSAC:
            entry = LogEntry.SACCENDR
        elif saccade.getEntryType() == LogEntry.LSAC:
            entry = LogEntry.SACCENDL
        else:
            raise ValueError("No saccade to init SaccadeEndEntry")
        super(SaccadeEndEntry, self).__init__(entry, start)
    
    ##
    # Creates a deepcopy of oneself
    def copy(self):
        return SaccadeEndEntry(self.saccade.copy())

    ##
    # Create a string from self in Eyelink ascii format
    def toAsc(self):
        esac = ""
        SEP = LogEntry.SEP
        if self.getEntryType() == LogEntry.SACCENDR:
            esac += ("ESACC" + SEP + "R" + SEP)
        elif self.getEntryType() == LogEntry.SACCENDL:
            esac += ("ESACC" + SEP + "L" + SEP)
        else:
            raise ValueError("invalid end saccade encountered")

        esac += ( str(int(self.saccade.getEyeTime()))   + SEP +   \
                  str(int(self.getEyeTime()))           + SEP +   \
                  str(int(self.saccade.duration))       + SEP +   \
                  str(self.saccade.xstart)              + SEP +   \
                  str(self.saccade.ystart)              + SEP +   \
                  str(self.saccade.xend)                + SEP +   \
                  str(self.saccade.yend)                + SEP +   \
                  str(int(self.saccade.duration))
                  )
        return esac

##
# This is a startentry for a fixation log. It is present in the log because
# it expands to some general information in an Eyelink ascii log
#
class StartEntry(LogEntry):
    '''
        This entry logs some shit that Fixation demands...
    '''
    # indicators for which eye is measured
    ## log uses left eye
    LEFT  = 1
    ## log uses right eye
    RIGHT = 2
    ## log uses both eyes
    BINO  = 3

    ##
    # Log some mess that fixation expects, but clutters your output...
    #
    # \param time the time of the log
    # \param eye must be StartEntr.LEFT, .RIGHT, or BINO, but I don't expect
    #  Fixation to understand about binocular data...
    # \param le default to windows line ending(works on most systems)
    def __init__(self, time, eye, le="\r\n"):
        ## tells which eye is present in data.
        self.eye = eye
        ## tells which line ending must be used
        self.le  = le
        super(StartEntry, self).__init__(LogEntry.BEGIN, time)
    
    def copy(self):
        return StartEntry(self.eyetime, self.eye, self.le)

    ##
    # Create a string from self in Eyelink ascii format
    def toAsc(self):
        ''' Return a ascii presentation of these events '''
        SEP = LogEntry.SEP
        start   = "START"   + SEP + str(int(self.getEyeTime())) + SEP
        samples = "SAMPLES" + SEP + "GAZE" + SEP
        events  = "EVENTS"  + SEP + "GAZE" + SEP
        postfix = "TRACKING" + SEP + "CR" + SEP + "FILTER" + SEP + "2"

        if self.eye == StartEntry.LEFT:
            start += "LEFT" + SEP
            # TODO hard coded "250" isn't really nice"
            events += SEP.join(["LEFT", "RATE", "250", postfix])
            samples += SEP.join(["LEFT", "HTARGET", "RATE", "250", postfix])
        elif self.eye == StartEntry.RIGHT:
            start += "RIGHT" + SEP
            events += SEP.join(["RIGHT", "RATE", "250", postfix])
            samples += SEP.join(["RIGHT", "HTARGET", "RATE", "250", postfix])
        elif self.eye == StartEntry.BINO:
            # NOTE Fixation tool doesn't know about this.
            start += "".join(["LEFT", SEP, "RIGHT", SEP])
            events += SEP.join(["LEFT", "RIGHT", "RATE", "250", postfix])
            samples += SEP.join(["LEFT", "RIGHT", "HTARGET", "RATE", "250", postfix])
        else:
            raise ValueError("Unknown eye\"type\"")

        start += SEP.join(["SAMPLES", "EVENTS"])
        #return start
        return self.le.join([start, events, samples])

##
# needed to mark an end in a Eyelink ascii log
class EndEntry(LogEntry):

    ##
    # Inits an end entry
    def __init__(self, time):
        super(EndEntry, self).__init__(LogEntry.END, time)
    
    def copy(self):
        return EndEntry(self.eyetime)

    ##
    # Create a string from self in Eyelink ascii format
    def toAsc(self):
        SEP = LogEntry.SEP
        string = "END" + SEP + str(int(self.getEyeTime())) + SEP + "SAMPLES" + SEP + "RES"
        return string


##
# Generator funtion that yields fixations
# @param entries a iterable of LogEntry
def generateFixations(entries):
    ''' Generates fixations '''
    for entry in entries:
        if entry.getEntryType() == LogEntry.LFIX or entry.getEntryType() == LogEntry.RFIX:
            yield entry

##
# Generator funtion that yields saccades
# @param entries a iterable of LogEntry
def generateSaccades(entries):
    ''' Generates saccades '''
    for entry in entries:
        if entry.getEntryType() == LogEntry.LSAC or entry.getEntryType() == LogEntry.RSAC:
            yield entry

##
# yields EndFixation marks for an Eyelink log
# @param entries a iterable of LogEntry
def generateNewEndfixations(entries):
    ''' Generates end fixations '''
    for fix in generateFixations(entries):
        yield EndFixation(fix)

##
# yields EndSaccade marks for an Eyelink log
# @param entries a iterable of LogEntry
def generateNewEndSaccades(entries):
    ''' Generates end saccades '''
    for sac in generateSaccades(entries):
        yield EndSaccade(sac)
##
# Generator for fixation of the lefteye
# @param entries a iterable of LogEntry
def generateLGaze(entries):
    for e in entries:
        if LogEntry.isLGaze(e):
            yield e

##
# Generator for fixation of the righteye
# @param entries a iterable of LogEntry
def generateRGaze(entries):
    for e in entries:
        if LogEntry.isRGaze(e):
            yield e


##
# Callable class to sort logentries for an Eyelink compatible log
class SortFixationLog:

    # These values are used to sort entries with an equal timestamp

    ## Entry with end.
    end   = 0
    ## Entry with msg.
    msg   = end   + 1
    ## Entry with start fixation left eye.
    sfixl = msg   + 1
    ## Entry with start fixation right eye.
    sfixr = sfixl + 1
    ## Entry with start saccade left eye.
    ssacl = sfixr + 1
    ## Entry with start saccade right eye.
    ssacr = ssacl + 1
    ## Entry with gaze.
    gaze  = ssacr + 1
    ## Entry with end fixation with right eye.
    efixr = gaze  + 1
    ## Entry with end fixation with left eye.
    efixl = efixr + 1
    ## Entry with end saccade with right eye.
    esacr = efixl + 1
    ## Entry with end saccade with left eye.
    esacl = esacr + 1
    ## Entry with start marker.
    start = esacl + 1
    ## Entry with .

    ##
    # this dictionary maps LogEntry.getEntryType() to above messages
    # so the above order is used for sorting.
    mapdict = {
        LogEntry.LFIX       : sfixl ,
        LogEntry.RFIX       : sfixr ,
        LogEntry.MESSAGE    : msg   ,
        LogEntry.LSAC       : ssacl ,
        LogEntry.RSAC       : ssacr ,
        LogEntry.ASCGAZE    : gaze  ,
        LogEntry.FIXENDR    : efixr ,
        LogEntry.FIXENDL    : efixl ,
        LogEntry.SACCENDR   : esacr ,
        LogEntry.SACCENDL   : esacl ,
        LogEntry.BEGIN      : start ,
        LogEntry.END        : end
    }

    ##
    # This method can be used by a sorting algoritm to sort entries
    # the items will be sorted on timestamp first and LogEntries with
    # equal timestamps will be sorten on entry type secondly.
    #
    # \todo When a key error occures raise a new exceptions, since it
    # is a programming and not a runtime error.
    def __call__(self, lefthandside, righthandside):
        diff = LogEntry.sortCallback(lefthandside, righthandside)
        if diff == 0:
            try:
                return self.mapdict[lefthandside.getEntryType()] -\
                       self.mapdict[righthandside.getEntryType()]
            except KeyError as e:
                print("left = ",lefthandside.getEntryType(), end=' ')
                print("\tright= ",righthandside.getEntryType())
        return diff

##
# Appends begin and end entries to a Eyelink ascii log
def _appendBeginEndEntries(entries, eye):
    import re

    ## Can be used as test to filter a list of entries with trials
    # that contain a line with trialbeg
    class FilterTrialBegin:
        regex = re.compile(r"^trialbeg\s+\d+\s+\d+\s+\d+\s+([a-zA-Z]+)$")
        def __call__(self, entry):
            m = self.regex.match(entry.message)
            if m:
                if m.group(1) != "FILL":
                    return True
            return False

    ## Can be used as test to filter a list of entries with trials
    # that contain a line with trialend
    class FilterTrialEnd:
        regex = re.compile(r"^trialend\s+\d+\s+\d+\s+\d+\s+([a-zA-Z]+)$")
        def __call__(self, entry):
            m = self.regex.match(entry.message)
            if m:
                if m.group(1) != "FILL":
                    return True
            return False

    filtlist= list(filter(LogEntry.isMessage, entries))
    begins  = list(filter(FilterTrialBegin(), filtlist))
    ends    = list(filter(FilterTrialEnd(), filtlist))
    for i in begins:
        entries.append (StartEntry(i.getEyeTime(), eye))
    for i in ends:
        entries.append (EndEntry(i.getEyeTime()))


##
# This function examines the gaze data. Creates it's own fixations and saccades
# and tries to log all those events with the normal event to a file with filename
# filename.
# @param entries
# @param filename
def saveForFixation(entries, filename):

    f = open(filename, "wb")

    # create end events for fixations and saccades.
    endfixations = []
    for fix in generateFixations(entries):
        endfixations.append(FixationEndEntry(fix))
    endsaccades = []
    for sac in generateSaccades(entries):
        endsaccades.append(SaccadeEndEntry(sac))

    entries.extend(endfixations)
    entries.extend(endsaccades)

    # generate AscGazeEntries
    for i, j in itertools.zip_longest(generateLGaze(entries), generateRGaze(entries)):
        entries.append( AscGazeEntry(i, j) )

    eyetype = StartEntry.LEFT
    for e in reversed(entries):
        if e.getEntryType() == LogEntry.ASCGAZE:
            if e.lgaze and e.rgaze:
                eyetype = StartEntry.BINO
            elif e.lgaze:
                eyetype = StartEntry.LEFT
            elif e.rgaze:
                eyetype = StartEntry.RIGHT
            else:
                raise ValueError("invalid AscGazeEntry encountered")
            break

    _appendBeginEndEntries(entries, eyetype)

    #remove ordinary gaze data to keep fixation compatible gazedata
    filtobj = lambda e: not LogEntry.isGaze(e)
    entries = list(filter(filtobj, entries))

    entries.sort(key=functools.cmp_to_key(SortFixationLog()))
    for i in entries:
        f.write((i.toAsc() + "\r\n").encode('utf8'))
    f.close()
