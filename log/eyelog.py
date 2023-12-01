#!usr/bin/env python
"""Contains classes/function for building an eyemovement log

This is a module that contains all classes needed to create a log file for the
analysis of behavioral experiments that contain eye movement data.

In theory an experiment consists of a series of trials ``log.eyexperiment.Eyetrials``.
In a trial are a number of events that can occur. Events are for example samples
of the eye tracker, fixations, saccades etc. An event is characterized by a
time stamp and a type. Depending on the type there is also other data relevant.
Events will be primarily sorted on time stamp and then on the type.
"""

##
# \file eyelog.py
# This file contains utilities for log files.
#

from __future__ import annotations

import itertools
import functools
import abc
import sys
import typing
if sys.version_info >= (3, 9):
    from collections.abc import Iterable
else:
    from typing import Iterable


class LogEntry (abc.ABC):
    """LogEntry, an abstract base class for all LogEntries in an eyelog.

    A logentry communicates which event occurred, and at which time.
    """
    # TODO ENTRIES by number are nice, however, inconvenient when new
    # entry types are added. Priorly, we didn't have L- and RBLINKS, because
    # I added them, I had to increment all events below RBLINk by two.
    #
    # That is not to bad, however, that also invalidates log written
    # before blinks were added, and that is not so nice.

    ## Entry is a sample of the left eye
    LGAZE = 0
    ## Entry that describes a right gaze sample
    RGAZE = 1

    ## Entry that describes a left fixation
    LFIX = 2
    ## Entry that describes a right fixation
    RFIX = 3

    # The left eye blinks (or is not detected)
    LBLINK = 4
    # The right eye blinks (or is not detected)
    RBLINK = 5

    ## Entry that describes a stimulus
    STIMULUS = 6
    ## Entry that describes a user defined message
    MESSAGE = 7
    ## Entry that describes a saccade of the left eye
    LSAC = 8
    ## Entry that descibes a saccade of the right eye
    RSAC = 9

    # extended types these don't belong to a log, but can be handy for unhandy
    # formats that log a end event, or do some other marking like Begin and end

    ## Is a gaze in a eyelink asc log
    ASCGAZE = 10
    ## Is a Eyelink fixation end in a asc log of the left eye
    FIXENDL = 11
    ## Is a Eyelink fixation end in a asc log of the right eye
    FIXENDR = 12
    ## Is a saccade end in an asc log of the left eye.
    SACCENDL = 13
    ## Is a saccade end in an asc log of the right eye.
    SACCENDR = 14

    ## marks the end of a blink of the in an asc log
    BLINKENDL = 15
    ## marks the end of a blink of the in an asc log
    BLINKENDR = 16

    ## Mark a begin in a ascii log
    BEGIN = 17
    ## Mark an end in a ascii log
    END = 18

    ## The separator used to separate columns.
    SEP = '\t'

    ## Construct an instance of LogEntry
    #
    # @param entrytype defines what kind of log entry this is.
    # @param eyetime A float that marks the time in the time of the eyetracker.
    def __init__(self, entrytype, eyetime):
        ## The type of entry of this LogEntry
        self.entrytype = entrytype
        self.eyetime = eyetime

    ## Tell what kind of LogEntry this is.
    def getEntryType(self):
        return self.entrytype

    ## Compares for object equality
    def __eq__(self, other):
        return type(self) is type(other) and self.__dict__ == other.__dict__

    ## Compares for object difference
    def __ne__(self, other):
        return not self == other

    ## This marks the time point in milliseconds when the event happened
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
        """Implement return of string in format as Eyelink edf to ascii does.
        """

    ##
    # Create a deep copy of this instance
    #
    @abc.abstractmethod
    def copy(self):
        pass

#    @abstractmethod
#    def __str__():
#        """ Implement return of string in format as Eyelink edf to ascii does. """
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
        """ Determines whether a LogEntry is a fixaton """
        return entry.getEntryType() == LogEntry.LFIX or entry.getEntryType() == LogEntry.RFIX

    ## Returns True if this is a saccade
    @staticmethod
    def isSaccade(entry):
        """ Determines whether a LogEntry is a saccade """
        return entry.getEntryType() == LogEntry.LSAC or entry.getEntryType() == LogEntry.RSAC

    @staticmethod
    def isBlink(entry: LogEntry) -> bool:
        """isBlink determines whether entry is a blink.

        :param entry: The logentry to investigate
        :type entry: LogEntry
        :rtype: bool
        """
        return entry.getEntryType() in [LogEntry.LBLINK, LogEntry.RBLINK]

    ## Returns True if this is a message entry
    @staticmethod
    def isMessage(entry):
        return entry.getEntryType() == LogEntry.MESSAGE

    ## Function useful for removing fixations and or saccades from the log.
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
        return list(
            filter(lambda e: not e.getEntryType() == LogEntry.LGAZE, entries)
        )

    ##
    # Removes the right gaze entries
    #
    # can be used to obtain a list without the right gaze """
    # \param entries an iterable
    @staticmethod
    def removeRightGaze(entries):
        return list(
            filter(lambda e: not e.getEntryType() == LogEntry.RGAZE, entries)
        )


##
# This describes a left or right eye gaze sample of the eyetracker.
class GazeEntry(LogEntry):

    ACCEPTABLE_ENTRIES = [
        LogEntry.LGAZE,
        LogEntry.RGAZE
    ]

    ##
    # construct a GazeEntry
    #
    # \param entrytype LogEntry.RGAZE or LogEntry.LGaze
    # \param eyetime the time on the eyetracker when the gaze was sampled
    # \param x float of the x-coordinate of the gaze
    # \param y float of the y-coordinate of the gaze
    # \param pupil the pupilsize during the gazesample
    def __init__(self, entrytype, eyetime, x, y, pupil):
        if entrytype not in GazeEntry.ACCEPTABLE_ENTRIES:
            raise ValueError("entrytype should be L- or RGAZE")
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
        return GazeEntry(
            self.entrytype, self.eyetime, self.x, self.y, self.pupil
        )

    ##
    # Create a string from self in Eyelink ascii format
    def toAsc(self):
        raise ValueError("GazeEntries should not be converted to .asc format")


class AscGazeEntry(LogEntry):
    """An entry in a logfile that logs the gaze compatible for Fixation
    program(Cozijn)

    In this type of GazeEntry, both the signal of the left and right
    eye are encoded in the same log entry, in contrast with iSpectors default
    GazeEntry, with encode the left or right eye.
    """

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

    def copy(self):
        """Create a deep copy the asc gaze entry"""
        return AscGazeEntry(self.lgaze, self.rgaze)

    def toAsc(self):
        """Create a string from self in Eyelink ascii format"""
        string = str(int(self.getEyeTime()))
        SEP = LogEntry.SEP
        # TODO check if fixation performs better if times are in integers
        if self.lgaze:
            string += "".join(
                [
                    SEP, str(self.lgaze.x),
                    SEP, str(self.lgaze.y),
                    SEP, str(self.lgaze.pupil)
                ]
            )
        if self.rgaze:
            string += "".join(
                [
                    SEP, str(self.rgaze.x),
                    SEP, str(self.rgaze.y),
                    SEP, str(self.rgaze.pupil)
                ]
            )
        return string


class FixationEntry(LogEntry):
    """A FixationEntry Describes a fixation of the left or right eye

    A fixation is determined by a location on a 2D plane and ,its time
    and the duration of the fixation.
    """

    ACCEPTABLE_ENTRIES = [
        LogEntry.LFIX,
        LogEntry.RFIX
    ]

    def __init__(self, entrytype, eyetime, eyedur, x, y):
        """Init a fixation entry

        @param entrytype  Must be LogEntry.LFIX or LogEntry.RFIX
        @param eyetime    The time (ms) on the eyetracker when the fixation starts
        @param eyedur     The duration of the fixation.
        @param x          The x coordinate of the fixation
        @param y          The y coordinate of the fixation
        """
        if entrytype not in FixationEntry.ACCEPTABLE_ENTRIES:
            raise ValueError("entrytype should be LFIX or RFIX")
        super().__init__(entrytype, eyetime)
        self.x = x
        ## the y coordinate of this fixation
        self.y = y
        ## the duration of this fixation
        self.duration = eyedur

    def copy(self):
        """Create a deepcopy of oneself"""
        return FixationEntry(
            self.entrytype, self.eyetime, self.duration, self.x, self.y
        )

    def toAsc(self):
        """Create a string from self in Eyelink ascii format"""
        ssac = ""
        if self.getEntryType() == LogEntry.LFIX:
            ssac = "SFIX\tL\t"
        else:
            ssac = "SFIX\tR\t"
        return ssac + str(int(self.getEyeTime()))


class FixationEndEntry(LogEntry):
    """This class can be used to mark fixation ends in an asc log."""

    def __init__(self, fixation):
        """@param fixation a valid FixationEntry"""
        ## The FixationEntry that belongs to this end entry.
        self.fixation = fixation
        time = fixation.getEyeTime() + fixation.duration
        entry = None
        if fixation.getEntryType() == LogEntry.LFIX:
            entry = LogEntry.FIXENDL
        elif fixation.getEntryType() == LogEntry.RFIX:
            entry = LogEntry.FIXENDR
        else:
            raise ValueError(
                "Fixation entry should be initialized with LFIX or RFIX"
            )
        super(FixationEndEntry, self).__init__(entry, time)

    def copy(self):
        """create a deepcopy of oneself"""
        return FixationEntry(self.fixation)

    def toAsc(self):
        """Create a string from self in Eyelink ascii format"""
        efix = ""
        if self.getEntryType() == LogEntry.FIXENDL:
            efix = "EFIX\tL"
        elif self.getEntryType() == LogEntry.FIXENDR:
            efix = "EFIX\tR"
        else:
            raise ValueError("Wrong entry type in FixationEndEntry")

        SEP = LogEntry.SEP
        return "".join(
            [
                efix,
                SEP, str(int(self.fixation.getEyeTime())),
                SEP, str(int(self.getEyeTime())),
                SEP, str(int(self.fixation.duration)),
                SEP, str(self.fixation.x),
                SEP, str(self.fixation.y),
                SEP, str(int(self.fixation.duration))
            ]
        )


class MessageEntry(LogEntry):
    """A logged user defined message in a string."""
    def __init__(self, eyetime, message):
        """Initialize a MessageEntry

        @param eyetime the time of the message in eyetracking time
        @param message a used defined string
        """
        super(MessageEntry, self).__init__(LogEntry.MESSAGE, eyetime)
        ## the message of this Message entry
        self.message = message

    def copy(self):
        """Return a deepcopy of the message entry"""
        return MessageEntry(self.eyetime, str(self.message))

    def toAsc(self):
        """Create a string from self in Eyelink ascii format"""
        SEP = LogEntry.SEP
        return "".join(
            ["MSG", SEP, str(int(self.getEyeTime())), SEP, self.message]
        )


class SaccadeEntry(LogEntry):
    """SaccadeEntry This describes a saccade in an experiment

    A saccade is defined by its eye, a starttime, duration and start and end
    position
    """

    ACCEPTABLE_ENTRIES = [
        LogEntry.LSAC,
        LogEntry.RSAC
    ]

    def __init__(self,
                 et,
                 eyetime,
                 duration,
                 xstart,
                 ystart,
                 xend,
                 yend
                 ):
        """Initialize a SaccadeEntry

        @param et must be LogEntry.LSAC or LogEntry.RSAC
        @param eyetime the time (ms) on eyetracker when the saccade started
        @param duration the duration(ms) of the saccade
        @param xstart starting x coordinate.
        @param ystart starting y coordinate.
        @param xend end x coordinate.
        @param yend end y coordinate.
        """
        if et not in SaccadeEntry.ACCEPTABLE_ENTRIES:
            raise ValueError("entrytype should be L- or RSAC")
        super(SaccadeEntry, self).__init__(et, eyetime)
        ## x coordinate of the start
        self.xstart = xstart
        ## y coordinate of the start
        self.ystart = ystart
        ## x coordinate of the end position
        self.xend = xend
        ## y coordinate of the end position
        self.yend = yend
        ## duration of the saccade in ms.
        self.duration = duration

    def copy(self):
        """create a deep copy of oneself"""
        return SaccadeEntry(
            self.entrytype, self.eyetime, self.duration,
            self.xstart, self.ystart, self.xend, self.yend
        )

    def toAsc(self):
        """Create a string from self in Eyelink ascii format."""
        string = ""
        SEP = LogEntry.SEP
        if self.getEntryType() == LogEntry.RSAC:
            string += ("SSACC" + SEP + "R" + SEP + str(int(self.getEyeTime())))
        elif self.getEntryType() == LogEntry.LSAC:
            string += ("SSACC" + SEP + "L" + SEP + str(int(self.getEyeTime())))
        else:
            raise ValueError("Unknown entry type")
        return string


class SaccadeEndEntry(LogEntry):
    """A marker for saccade end in a Eyelink ascii log."""

    def __init__(self, saccade: SaccadeEntry):
        """inits a SaccadeEndEntry"""

        if not isinstance(saccade, SaccadeEntry):
            raise TypeError("saccade should be an instance of SaccadeEntry")

        ## the saccade that belong to this end marker
        self.saccade = saccade
        start = saccade.getEyeTime() + saccade.duration

        endsac = {
            LogEntry.LSAC: LogEntry.SACCENDL,
            LogEntry.RSAC: LogEntry.SACCENDR
        }
        entry = endsac[saccade.getEntryType()]
        super(SaccadeEndEntry, self).__init__(entry, start)

    def copy(self):
        """Creates a deepcopy of oneself"""
        return SaccadeEndEntry(self.saccade.copy())

    def toAsc(self):
        """Create a string from self in Eyelink ascii format"""
        esac = ""
        SEP = LogEntry.SEP
        if self.getEntryType() == LogEntry.SACCENDR:
            esac += ("ESACC" + SEP + "R" + SEP)
        elif self.getEntryType() == LogEntry.SACCENDL:
            esac += ("ESACC" + SEP + "L" + SEP)
        else:
            raise ValueError("invalid end saccade encountered")

        esac += "".join(
            [
                str(int(self.saccade.getEyeTime())), SEP,
                str(int(self.getEyeTime())), SEP,
                str(int(self.saccade.duration)), SEP,
                str(self.saccade.xstart), SEP,
                str(self.saccade.ystart), SEP,
                str(self.saccade.xend), SEP,
                str(self.saccade.yend), SEP,
                str(int(self.saccade.duration))
            ]
        )
        return esac


class BlinkEntry(LogEntry):
    """BlinkEntry marks a blink in a logfile"""

    ACCEPTABLE_ENTRIES = [
        LogEntry.LBLINK,
        LogEntry.RBLINK
    ]

    def __init__(self, entrytype, eyetime: float, dur: float):
        """Initializes a blink entry.

        :param entrytype: One out of ACCEPTABLE_ENTRIES
        :param eyetime: The time at which the blink started
        :type eyetime: float
        :param dur: The duration of the blink
        :type dur: float
        """
        if entrytype not in BlinkEntry.ACCEPTABLE_ENTRIES:
            raise ValueError("entrytype should be LBLINK or RBLINK")
        super().__init__(entrytype, eyetime)
        self.duration = dur

    def copy(self):
        """Creates a deepcopy of oneself"""
        return BlinkEntry(self.getEntryType(), self.getEyeTime(), self.duration)

    def toAsc(self):
        """Create a string from self in Eyelink ascii format"""
        sblink = ""
        SEP = LogEntry.SEP
        if self.getEntryType() == LogEntry.RBLINK:
            sblink += ("SBLINK" + SEP + "R" + SEP)
        elif self.getEntryType() == LogEntry.LBLINK:
            sblink += ("SBLINK" + SEP + "L" + SEP)
        else:
            raise ValueError("invalid sblink encountered")

        sblink += str(self.getEyeTime())
        return sblink


class BlinkEndEntry(LogEntry):
    """BlinkEndEntry marks the end of a blink in an eyelink asc log."""

    def __init__(self, startentry: BlinkEntry):
        et = LogEntry.BLINKENDR
        if startentry.getEntryType() == LogEntry.LBLINK:
            et = LogEntry.BLINKENDL

        super().__init__(et, startentry.getEyeTime() + startentry.duration)
        self.startentry = startentry

    def copy(self):
        """Creates a deepcopy of oneself"""
        return BlinkEndEntry(self.startentry.copy())

    def toAsc(self):
        """Create a string from self in Eyelink ascii format"""
        eblink = ""
        SEP = LogEntry.SEP
        if self.getEntryType() == LogEntry.BLINKENDR:
            eblink += ("EBLINK" + SEP + "R" + SEP)
        elif self.getEntryType() == LogEntry.BLINKENDL:
            eblink += ("EBLINK" + SEP + "L" + SEP)
        else:
            raise ValueError("invalid sblink encountered")

        eblink += "".join(
            [
                str(int(self.startentry.getEyeTime())), SEP,
                str(int(self.getEyeTime())), SEP,
                str(int(self.startentry.duration))
            ]
        )
        return eblink


class StartEntry(LogEntry):
    """This is a startentry for a fixation log.

    It is present in the log because it expands to some general information in
    an Eyelink ascii log. This entry logs some shit that Fixation demands...
    """
    # indicators for which eye is measured
    ## log uses left eye
    LEFT = 1
    ## log uses right eye
    RIGHT = 2
    ## log uses both eyes
    BINO = 3

    def __init__(self, time, eye, le="\r\n"):
        """Log some mess that fixation expects, but clutters your output...

        @param time the time of the log
        @param eye must be StartEntr.LEFT, .RIGHT, or BINO, but I don't expect
         Fixation to understand about binocular data...
        @param le default to windows line ending(works on most systems)
        """
        ## tells which eye is present in data.
        self.eye = eye
        ## tells which line ending must be used
        self.le = le
        super(StartEntry, self).__init__(LogEntry.BEGIN, time)

    def copy(self):
        """Create a deepcopy of oneself"""
        return StartEntry(self.eyetime, self.eye, self.le)

    def toAsc(self):
        """ Return a ascii presentation of these events """
        SEP = LogEntry.SEP
        start = "START" + SEP + str(int(self.getEyeTime())) + SEP
        samples = "SAMPLES" + SEP + "GAZE" + SEP
        events = "EVENTS" + SEP + "GAZE" + SEP
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
            samples += SEP.join(
                ["LEFT", "RIGHT", "HTARGET", "RATE", "250", postfix]
            )
        else:
            raise ValueError("Unknown eye\"type\"")

        start += SEP.join(["SAMPLES", "EVENTS"])
        return self.le.join([start, events, samples])


class EndEntry(LogEntry):
    """needed to mark an end in a Eyelink ascii log."""

    def __init__(self, time):
        """Inits an end entry"""
        super(EndEntry, self).__init__(LogEntry.END, time)

    def copy(self):
        """Creates a deepcopy of oneself"""
        return EndEntry(self.eyetime)

    def toAsc(self):
        """Create a string from self in Eyelink ascii format."""
        SEP = LogEntry.SEP
        string = SEP.join(
            ["END", str(int(self.getEyeTime())), "SAMPLES", "RES"]
        )
        return string


logentry_iterable = Iterable[LogEntry]


def generateFixations(entries: logentry_iterable):
    """Generator function that yields fixations from a logentry_iterable"""
    fixentries = [LogEntry.LFIX, LogEntry.RFIX]
    for entry in entries:
        if entry.getEntryType() in fixentries:
            yield entry


def generateSaccades(entries: logentry_iterable):
    """Generator function that yields saccades from a logentry_iterable"""
    sacentries = [LogEntry.LSAC, LogEntry.RSAC]
    for entry in entries:
        if entry.getEntryType() in sacentries:
            yield entry


def generateBlinks(entries: logentry_iterable):
    """Generator function that yields blinks from a logentry_iterable"""
    for entry in entries:
        if isinstance(entry, BlinkEntry):
            yield entry


def generateNewEndfixations(entries: logentry_iterable):
    """yields EndFixation marks for an Eyelink log"""
    for fix in generateFixations(entries):
        yield FixationEndEntry(fix)


def generateNewEndSaccades(entries: logentry_iterable):
    """yields EndSaccade marks for an Eyelink log"""
    for sac in generateSaccades(entries):
        yield SaccadeEndEntry(sac)


def generateEndBlinks(entries: logentry_iterable):
    """yields a end entries for entries"""
    for blink in generateBlinks(entries):
        yield BlinkEndEntry(blink)


def generateLGaze(entries: logentry_iterable):
    """Generator for fixation of the lefteye"""
    for e in entries:
        if LogEntry.isLGaze(e):
            yield e


def generateRGaze(entries: logentry_iterable):
    """Generator for gaze samples of the righteye"""
    for e in entries:
        if LogEntry.isRGaze(e):
            yield e


def generateAscGazeEntries(
        entries: logentry_iterable) -> typing.Generator[
            AscGazeEntry, None, None]:
    """Filters AscGazeEntries from entries"""
    for e in entries:
        if isinstance(e, AscGazeEntry):
            yield e


class SortFixationLog:
    """Callable class to sort logentries for an Eyelink compatible log"""

    # These values are used to sort entries with an equal timestamp

    ## Entry with end.
    end = 0
    ## Entry with msg.
    msg = end + 1
    ## Entry with start fixation left eye.
    sfixl = msg + 1
    ## Entry with start fixation right eye.
    sfixr = sfixl + 1
    ## Entry with start saccade left eye.
    ssacl = sfixr + 1
    ## Entry with start saccade right eye.
    ssacr = ssacl + 1
    ## Entry with start blink left eye
    sblinkl = ssacr + 1
    ## Entry with start blink right eye
    sblinkr = sblinkl + 1
    ## Entry with gaze.
    gaze = sblinkr + 1
    ## Entry with end fixation with right eye.
    efixr = gaze + 1
    ## Entry with end fixation with left eye.
    efixl = efixr + 1
    ## Entry with end saccade with right eye.
    esacr = efixl + 1
    ## Entry with end saccade with left eye.
    esacl = esacr + 1
    ## Entry with end blink with right eye.
    eblinkr = esacl + 1
    ## Entry with end blink with left eye.
    eblinkl = eblinkr + 1
    ## Entry with start marker.
    start = eblinkl + 1

    ##
    # this dictionary maps LogEntry.getEntryType() to above messages
    # so the above order is used for sorting.
    mapdict = {
        LogEntry.LFIX: sfixl,
        LogEntry.RFIX: sfixr,
        LogEntry.MESSAGE: msg,
        LogEntry.LSAC: ssacl,
        LogEntry.RSAC: ssacr,
        LogEntry.LBLINK: sblinkl,
        LogEntry.RBLINK: sblinkr,
        LogEntry.ASCGAZE: gaze,
        LogEntry.FIXENDR: efixr,
        LogEntry.FIXENDL: efixl,
        LogEntry.SACCENDR: esacr,
        LogEntry.SACCENDL: esacl,
        LogEntry.BLINKENDR: eblinkr,
        LogEntry.BLINKENDL: eblinkl,
        LogEntry.BEGIN: start,
        LogEntry.END: end
    }

    def __call__(self, lefthandside, righthandside):
        """This method can be used by a sorting algorithm to sort collections of
        LogEntry.

        The items will be sorted on timestamp first and LogEntries with
        equal timestamps will be sorted on entry type secondly.
        """
        diff = LogEntry.sortCallback(lefthandside, righthandside)
        if diff == 0:
            return self.mapdict[lefthandside.getEntryType()] -\
                self.mapdict[righthandside.getEntryType()]
        return diff


def _appendBeginEndEntries(entries, eye):
    """Appends begin and end entries to a Eyelink ascii log."""
    import re

    class FilterTrialBegin:
        """This class may be used as test to filter a list of entries with
        trials that contain a line with trialbeg
        """
        regex = re.compile(r"^trialbeg\s+\d+\s+\d+\s+\d+\s+([a-zA-Z]+)$")

        def __call__(self, entry):
            m = self.regex.match(entry.message)
            if m:
                if m.group(1) != "FILL":
                    return True
            return False

    class FilterTrialEnd:
        """This class may be used as test to filter a list of entries with
        trials that contain a line with trialend
        """
        regex = re.compile(r"^trialend\s+\d+\s+\d+\s+\d+\s+([a-zA-Z]+)$")

        def __call__(self, entry):
            m = self.regex.match(entry.message)
            if m:
                if m.group(1) != "FILL":
                    return True
            return False

    filtlist = list(filter(LogEntry.isMessage, entries))
    begins = list(filter(FilterTrialBegin(), filtlist))
    ends = list(filter(FilterTrialEnd(), filtlist))
    for i in begins:
        entries.append(StartEntry(i.getEyeTime(), eye))
    for i in ends:
        entries.append(EndEntry(i.getEyeTime()))


def saveForFixation(entries: typing.List[LogEntry], filename: str):
    """This function examines the gaze data. Creates it's own fixations and
    saccades and tries to log all those events with the normal event to a file
    with file name.

    @param entries
    @param filename
    """

    f = open(filename, "wb")

    # create end events for fixations and saccades.
    endfixations = []
    for fix in generateFixations(entries):
        endfixations.append(FixationEndEntry(fix))
    endsaccades = []
    for sac in generateSaccades(entries):
        endsaccades.append(SaccadeEndEntry(sac))
    endblinks: typing.List[BlinkEndEntry] = []
    endblinks += list(generateEndBlinks(entries))

    entries.extend(endfixations)
    entries.extend(endsaccades)
    entries.extend(endblinks)

    # generate AscGazeEntries
    for i, j in itertools.zip_longest(generateLGaze(entries), generateRGaze(entries)):
        entries.append(AscGazeEntry(i, j))

    eyetype = StartEntry.LEFT
    for e in generateAscGazeEntries(entries):
        # this makes sure the type is right.
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

    # remove ordinary gaze data to keep fixation compatible gazedata
    entries = list(filter(lambda e: not LogEntry.isGaze(e), entries))

    entries.sort(key=functools.cmp_to_key(SortFixationLog()))
    for i in entries:
        f.write((i.toAsc() + "\r\n").encode('utf8'))
    f.close()
