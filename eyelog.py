#!usr/bin/env python

import itertools
from abc import abstractmethod
from abc import ABCMeta
import re

class LogEntry (object):
    
    __metaclass__ = ABCMeta
    
    # entry types
    LGAZE       = 0
    RGAZE       = 1
    LFIX        = 2
    RFIX        = 3
    STIMULUS    = 4
    MESSAGE     = 5
    LSAC        = 6
    RSAC        = 7

    # extended types these don't belong to a log, but can be handy for unhandy formats
    # that log a end event, or do some other marking like Begin and end
    
    ASCGAZE = 8
    FIXENDL = 9
    FIXENDR = 10 
    SACCENDL= 11
    SACCENDR= 12
    BEGIN   = 13
    END     = 14

    #separator
    SEP     = '\t'
    
    def __init__(self, entrytype, zeptime, eyetime):
        self.entrytype  = entrytype
        self.zeptime    = zeptime
        self.eyetime    = eyetime

    def getEntryType(self) :
        return self.entrytype

    def getZepTime(self):
        return  self.zeptime

    def getEyeTime(self):
        return self.eyetime

    def sortCallback(el, er):
        diff = el.getEyeTime() - er.getEyeTime()
        if diff < 0:
            return -1
        elif diff == 0:
            return 0
        else:
            return 1

    @abstractmethod
    def toAsc():
        ''' Implement return of string in format as Eyelink edf to ascii does. '''
        pass
    
#    @abstractmethod
#    def __str__():
#        ''' Implement return of string in format as Eyelink edf to ascii does. '''
#        pass

    @staticmethod
    def isLGaze(entry):
        return entry.getEntryType() == LogEntry.LGAZE
        
    @staticmethod
    def isRGaze(entry):
        return entry.getEntryType() == LogEntry.RGAZE

    @staticmethod
    def isGaze(entry):
        return LogEntry.isLGaze(entry) or LogEntry.isRGaze(entry)

    @staticmethod
    def isFixation(entry):
        ''' Determines whether a LogEntry is a fixaton '''
        return entry.getEntryType() == LogEntry.LFIX or entry.getEntryType() == LogEntry.RFIX

    @staticmethod
    def isSaccade(entry):
        ''' Determines whether a LogEntry is a saccade '''
        return entry.getEntryType() == LogEntry.LSAC or entry.getEntryType() == LogEntry.RSAC
    
    @staticmethod
    def isMessage(entry):
        return entry.getEntryType() == LogEntry.MESSAGE

    @staticmethod
    def _removeEyeEvents(entry):
        return not (LogEntry.isFixation(entry) or LogEntry.isSaccade(entry))
    
    @staticmethod
    def removeEyeEvents(entries):
        '''
        removes fixations and saccades from the entries 
        @param entries a list with LogEntries
        @returns list of filtered entries.
        '''
        entries = filter(LogEntry._removeEyeEvents, entries)
        return entries

    @staticmethod
    def removeLeftGaze(entries):
        ''' can be used to obtain a list without the left gaze '''
        filt = lambda e: not e.getEntryType() == LogEntry.LGAZE
        return filter(filt, entries)
    
    @staticmethod
    def removeRightGaze(entries):
        ''' can be used to obtain a list without the right gaze '''
        filt = lambda e: not e.getEntryType() == LogEntry.RGAZE
        return filter(filt, entries)
    
class GazeEntry(LogEntry) :
    
    def __init__(self, entrytype, zeptime, eyetime, x, y, pupil) :
        super(GazeEntry, self).__init__(entrytype, zeptime, eyetime)
        self.x = x
        self.y = y
        self.pupil = pupil

    def toAsc(self):
        raise ValueError("GazeEntries should not be converted to .asc format")

class AscGazeEntry(LogEntry):
    ''' An entry in a logfile that logs the gaze compatible for Fixation program(Cozijn)
    '''
    def __init__(self, lgaze, rgaze):
        time = None
        if lgaze:
            time = lgaze.getEyeTime()
        elif rgaze:
            time = rgaze.getEyeTime()
        else:
            raise ValueError("Both lgaze and rgaze are not valid")
        super(AscGazeEntry, self).__init__(LogEntry.ASCGAZE, time, time)
        self.lgaze = lgaze
        self.rgaze = rgaze

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

class FixationEntry(LogEntry):
    
    def __init__(self, entrytype, zeptime, eyetime, eyedur, x, y):
        super(FixationEntry,self).__init__(entrytype, zeptime, eyetime)
        self.x = x
        self.y = y
        self.duration = eyedur

    def toAsc(self):
        ssac = ""
        if self.getEntryType() == LogEntry.LFIX:
            ssac = "SFIX\tL\t" 
        else:
            ssac = "SFIX\tR\t"
        return ssac + str(int(self.getEyeTime()))

class FixationEndEntry(LogEntry):
    
    def __init__(self, fixation):
        self.fixation = fixation
        time = fixation.getEyeTime() + fixation.duration
        entry = None
        if fixation.getEntryType() == LogEntry.LFIX:
            entry = LogEntry.FIXENDL
        elif fixation.getEntryType() == LogEntry.RFIX:
            entry = LogEntry.FIXENDR
        else:
            raise ValueError("Fixation entry should be initialized with LFIX or RFIX")
        super(FixationEndEntry, self).__init__(entry, time, time)
       
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

class MessageEntry(LogEntry):
    
    def __init__(self, zeptime, eyetime, message):
        super(MessageEntry, self).__init__(LogEntry.MESSAGE, zeptime, eyetime)
        self.message = message

    def toAsc(self):
        return "MSG" + "\t" + str(int(self.getEyeTime())) + "\t" + self.message

class SaccadeEntry(LogEntry):
    
    def __init__(self,
                 et,
                 zeptime,
                 eyetime,
                 duration,
                 xstart,
                 ystart,
                 xend,
                 yend
                 ):
        super(SaccadeEntry, self).__init__(et, zeptime, eyetime)
        self.xstart = xstart
        self.ystart = ystart
        self.xend   = xend
        self.yend   = yend
        self.duration = duration

    def toAsc(self):
        string =""
        SEP = LogEntry.SEP
        if self.getEntryType() == LogEntry.RSAC:
            string += ("SSAC" + SEP + "R" + SEP + str(int(self.getEyeTime())) )
        elif self.getEntryType() == LogEntry.LSAC:
            string += ("SSAC" + SEP + "L" + SEP + str(int(self.getEyeTime())) )
        else: raise ValueError("Unknown entry type")
        return string

class SaccadeEndEntry(LogEntry):
    
    def __init__(self, saccade):
        self.saccade = saccade
        start = saccade.getEyeTime() + saccade.duration
        entry = None
        if saccade.getEntryType() == LogEntry.RSAC:
            entry = LogEntry.SACCENDR
        elif saccade.getEntryType() == LogEntry.LSAC:
            entry = LogEntry.SACCENDL
        else:
            raise ValueError("No saccade to init SaccadeEndEntry")
        super(SaccadeEndEntry, self).__init__(entry, start, start)

    def toAsc(self):
        esac = ""
        SEP = LogEntry.SEP
        if self.getEntryType() == LogEntry.SACCENDR:
            esac += ("ESAC" + SEP + "R" + SEP)
        elif self.getEntryType() == LogEntry.SACCENDL:
            esac += ("ESAC" + SEP + "L" + SEP)
        else:
            raise ValueError("invalid end saccade encountered")
        
        esac += ( str(int(self.saccade.getEyeTime()))   + SEP +   \
                  str(int(self.getEyeTime()))           + SEP +   \
                  str(int(self.saccade.duration))       + SEP +   \
                  str(self.saccade.xstart)              + SEP +   \
                  str(self.saccade.ystart)              + SEP +   \
                  str(self.saccade.xend)                + SEP +   \
                  str(self.saccade.yend)                + SEP +   \
                  str(int(self.saccade.duration))       + SEP
                  )
        return esac

class StartEntry(LogEntry):
    '''
        This entry logs some shit that Fixation demands...
    '''
    # indicator for which eye is measured
    LEFT  = 1
    RIGHT = 2
    BINO  = 3
    
    def __init__(self, time, eye, le="\r\n"):
        ''' Log some mess that fixation expects, but clutters your output...
            @ param time the time of the log
            @ param eye must be StartEntr.LEFT, .RIGHT, or BINO, but I don't expect
              Fixation to understand about binocular data...
            @ param le default to windows line ending(works on most systems)
        '''
        self.eye = eye
        self.le  = le
        super(StartEntry, self).__init__(LogEntry.BEGIN, time, time)

    def toAsc(self):
        ''' Return a ascii presentation of these events '''
        SEP = LogEntry.SEP
        start   = "START"   + SEP + str(int(self.getEyeTime())) + SEP
        samples = "SAMPLES" + SEP + "GAZE" + SEP 
        events  = "EVENTS"  + SEP + "GAZE" + SEP
        postfix = "TRACKING" + SEP + "CR" + SEP + "FILTER" + SEP + "2"

        if self.eye == StartEntry.LEFT:
            start += "LEFT" + SEP
            #to do hard coded "250" isn't really nice"
            events += SEP.join(["LEFT", "RATE", "250", postfix])
            samples += SEP.join(["LEFT", "HTARGET", "RATE", "250", postfix])
        elif self.eye == StartEntry.RIGHT:
            start += "RIGHT" + SEP
            events += SEP.join(["RIGHT", "RATE", "250", postfix])
            samples += SEP.join(["RIGHT", "HTARGET", "RATE", "250", postfix])
        elif self.eye == StartEntry.BINO:
            # NOTE Fixation tool doesn't know about this.
            start += SEP.join(["LEFT","RIGHT"])
            events += SEP.join(["LEFT", "RIGHT", "RATE", "250", postfix])
            samples += SEP.join(["LEFT", "RIGHT", "HTARGET", "RATE", "250", postfix])
        else:
            raise ValueError("Unknown eye\"type\"")
        
        start += SEP.join(["SAMPLES", "EVENTS"])
        #return start
        return self.le.join([start, events, samples])

class EndEntry(LogEntry):
    
    def __init__(self, time):
        super(EndEntry, self).__init__(LogEntry.END, time, time)

    def toAsc(self):
        SEP = LogEntry.SEP
        string = "END" + SEP + str(int(self.getEyeTime())) + SEP + "SAMPLES" + SEP + "RES"
        return string


def generateFixations(entries):
    ''' Generates fixations '''
    for entry in entries:
        if entry.getEntryType() == LogEntry.LFIX or entry.getEntryType() == LogEntry.RFIX:
            yield entry

def generateSaccades(entries):
    ''' Generates saccades '''
    for entry in entries:
        if entry.getEntryType() == LogEntry.LSAC or entry.getEntryType() == LogEntry.RSAC:
            yield entry

def generateNewEndfixations(entries):
    ''' Generates end fixations '''
    for fix in generateFixations(entries):
        yield EndFixation(fix)

def generateNewEndSaccades(entries):
    ''' Generates end saccades '''
    for sac in generateSaccades(entries):
        yield EndSaccade(sac)

def generateLGaze(entries):
    for e in entries:
        if LogEntry.isLGaze(e):
            yield e

def generateRGaze(entries):
    for e in entries:
        if LogEntry.isRGaze(e):
            yield e

class FixationLog:
    ''' This class can transform an internal log to one compatible for Fixation '''
    _left = 0
    _right= 1
    _both = 2
    _empty= 3

    start = 0
    sfixl = start + 1
    sfixr = sfixl + 1
    ssacl = sfixr + 1
    ssacr = ssacl + 1
    gaze  = ssacr + 1
    esacr = gaze  + 1
    esacl = esacr + 1
    efixr = esacl + 1
    efixl = efixr + 1
    end   = efixl + 1

    def __init__(self, entries):
        self.logtype    = -1
        self.gaze       = []
        self.lfix       = []
        self.rfix       = []
        self.elfix      = []
        self.efix       = []
        self.lsac       = []
        self.rsac       = []
        self.elsac      = []
        self.ersac      = []
        self.messages   = []
        self._getGaze()

    def _getGaze(entries):
        left  = generateLGaze(entries)
        right = generateRGaze(entries)
        if len(left) == 0  and len(right) == 0:
            self.logtype = _empty
            return
        elif len(left) ==  len(right):
            self.logtype = _both
        elif len(left) > 0:
            self.logtype = _left
        else:
            self.logtype = _right

        for i,j in itertools.izip_longest(left,right):
            self.gaze.append( AscGazeEntry(i, j) )

class SortFixationLog:
    ''' Callable class to sort logentries for an Eyelink compatible log'''

    # These values are used to sort entries with an equal timestamp
    end   = 0
    msg   = end   + 1
    sfixl = msg   + 1
    sfixr = sfixl + 1
    ssacl = sfixr + 1
    ssacr = ssacl + 1
    gaze  = ssacr + 1
    efixr = gaze  + 1
    efixl = efixr + 1
    esacr = efixl + 1
    esacl = esacr + 1
    start = esacl + 1
    
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

    def __call__(self, lefthandside, righthandside):
        ''' is called by a sort algorithm firstly sort on time,
            if those are equal, sort on entry type
        '''
        diff = LogEntry.sortCallback(lefthandside, righthandside)
        if diff == 0:
            try:
                return self.mapdict[lefthandside.getEntryType()] -\
                       self.mapdict[righthandside.getEntryType()]
            except KeyError as e:
                print "left = ",lefthandside.getEntryType(),
                print "\tright= ",righthandside.getEntryType() 
        return diff

def _appendBeginEndEntries(entries, eye):
    import re
    class FilterTrialBegin:
        regex = re.compile(r"^trialbeg\s+\d+\s+\d+\s+\d+\s+([a-zA-Z]+)$")
        def __call__(self, entry):
            m = self.regex.match(entry.message)
            if m:
                if m.group(1) != "FILL":
                    return True
            return False
    
    class FilterTrialEnd:
        regex = re.compile(r"^trialend\s+\d+\s+\d+\s+\d+\s+([a-zA-Z]+)$")
        def __call__(self, entry):
            m = self.regex.match(entry.message)
            if m:
                if m.group(1) != "FILL":
                    return True
            return False

    filtlist= filter(LogEntry.isMessage, entries)
    begins  = filter(FilterTrialBegin(), filtlist)
    ends    = filter(FilterTrialEnd(), filtlist)
    for i in begins:
        entries.append (StartEntry(i.getEyeTime(), eye))
    for i in ends:
        entries.append (EndEntry(i.getEyeTime()))
    

def saveForFixation(entries, filename):
    ''' This function examines the gaze data. Creates it's own fixations and saccades
        and tries to log all those events with the normal event to a file with filename
        filename.
    '''
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
    for i, j in itertools.izip_longest(generateLGaze(entries), generateRGaze(entries)):
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
    entries = filter(filtobj, entries)

    entries.sort(SortFixationLog())
    for i in entries:
        f.write(i.toAsc() + "\r\n")
    f.close()

