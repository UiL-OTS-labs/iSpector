#!/usr/bin/env python

import re
from eyelog import *

def getLogEntry(splitline):
    n = int(splitline[0])
    l = splitline
    entry = None

    if n == LogEntry.LGAZE or n == LogEntry.RGAZE:
        entry = GazeEntry(int(l[0]),
                          float(l[1]),
                          float(l[2]),
                          float(l[3]),
                          float(l[4]),
                          float(l[5])
                          )
    elif n == LogEntry.LFIX or n == LogEntry.RFIX:
        e, zptime, eyetime, x, y, dur = int(l[0]),\
                                        float(l[1]),\
                                        float(l[2]),\
                                        float(l[3]),\
                                        float(l[4]),\
                                        float(l[5])

        entry = FixationEntry(e, zptime, eyetime, dur, x, y)
    
    elif n == LogEntry.STIMULUS:
        #FIXME
        raise RuntimeError("Implement the stimulus log entry")
    elif n == LogEntry.MESSAGE:
        #insert tabs back beyond l[3] and strip end of line chars
        stripped_string = "\t".join(l[3:]).strip("\r\n")
        entry = MessageEntry(float(l[1]),
                             float(l[2]),
                             stripped_string
                             )
    else:
        raise ValueError("Line: \"" + LogEntry.SEPARATOR.join(splitline) + "\" is invalid")
    return entry

def extractCsvLog(lines):
    logentries = []
    n = 1 # use this to mark location in file where the error is found
    for i in lines:
        try:
            splitline = i.split(LogEntry.SEP);
            logentries.append(getLogEntry(splitline))
        except Exception as e:
            raise ValueError("unable to parse line {1}: \"{0}\"".format(i, n) + str(e))
        n+=1
    return logentries

def extractAscLog(lines):
    '''
        Examines each line to check whether it has got valid input
        if so it appends it to the logentries
    '''
    logentries = []
    # asclog has no mention of time in zep or the program
    zeptime = -1.0
    #float between captured in regex group
    cflt = r"([-+]?[0-9]*\.?[0-9]+)"
    # match a message in the log
    msgre = re.compile(r"MSG\s+(\d+)\s+([^\r\n]*)")
    duosample = re.compile(
        r"^(\d+)\s+" + cflt + r"\s+" + cflt + r"\s+" + cflt + r"\s+" + cflt + r"\s+" + cflt + r"\s+" + cflt + r".+$"
        )
    #monosample would also match a duo sample(sample with both eyes, where the first three columns are assumed to be the left eye and the 2nd three columns belong to the right eye
    monosample = re.compile(r"^(\d+)\s+" + cflt + r"\s+" + cflt + r"\s+" + cflt + r".+$")
    #matches a end fixation, start fixations are ignorred
    endfix = re.compile(
        r"^EFIX\s+(R|L)\s+(\d+)\s+(\d+)\s+(\d+)\s+" + cflt + r"\s+" + cflt + r"\s+(\d+).*"
        )
    #this regex is used to determine whether monocular data is from the left or the right eye
    sampleformat = re.compile(r"^SAMPLES\s+GAZE\s+(\w+).+$")
    isleft = False

    #iterate over all lines and add relevant lines to the log
    for i in lines:
        m = msgre.search(i)
        if m:
            e  = MessageEntry(zeptime, float(m.group(1)), m.group(2))
            logentries.append(e)
            continue
        m = duosample.search(i)
        if m:
            #matched binocular sample
            try :
                eyetime = float(m.group(1))
                lx = float(m.group(2))
                ly = float(m.group(3))
                lp = float(m.group(4))
                rx = float(m.group(5))
                ry = float(m.group(6))
                rp = float(m.group(7))
                lgaze = GazeEntry(LogEntry.LGAZE, zeptime, eyetime, lx, ly, lp)
                rgaze = GazeEntry(LogEntry.RGAZE, zeptime, eyetime, rx, ry, rp)
                logentries.append(lgaze)
                logentries.append(rgaze)
            except ValueError as v:
                import traceback
                print i
                print traceback.print_exc()
            continue
        m = sampleformat.search(i)
        if m:
            #detect whether monocular data belongs to left or right eye
            lorr = m.group(1)
            isleft =  lorr.lower() == "right"
            continue
        m = monosample.search(i)
        if m:
            #matched monocular sample 
            eyetime = int(m.group(1))
            lx = float(m.group(2))
            ly = float(m.group(3))
            lp = float(m.group(4))
            #threat all gazes as left gazes
            gaze = None
            if isleft:
                gaze = GazeEntry(LogEntry.LGAZE, zeptime, eyetime, lx, ly, lp)
            else:
                gaze = GazeEntry(LogEntry.RGAZE, zeptime, eyetime, lx, ly, lp)
            logentries.append(gaze)
            continue
        m = endfix.search(i)
        if m:
            # detected fixation
            eyetype = m.group(1)
            fixstart = float(m.group(2))
            # eyeend = m.group(3) not used
            duration = float(m.group(4))
            x = float(m.group(5))
            y = float(m.group(6))
            fixentry = None
            if (eyetype == "R"):
                fixentry = FixationEntry(LogEntry.RFIX, zeptime, fixstart, duration, x, y)
            elif (eyetype == "L"):
                fixentry = FixationEntry(LogEntry.LFIX, zeptime, fixstart, duration, x, y)
            else:
                raise ValueError("Invalid fixation end: " + i)
            logentries.append(fixentry)
            continue
    return logentries


class ParseResult:

    """
    There can be many problems with parsing a file
    This class returns the files or error that have
    occured
    """

    def __init__(self, entries=[], errors=[]):
        """ """
        self.entries = entries
        self.errors = errors

    def setEntries(self, entries):
        self.entries = entries

    def getEntries(self):
        return self.entries

    def setErrors(self, errorlist):
        self.errorlist

    def appendError(self, error):
        self.errors.append(error)
        
    def getErrors(self):
        return self.errors


def parseEyeFile(filename):
    '''
    Parses the filename
    returns ParseResult
    '''
    CsvError = "Unable to parse file '{0}' as .csv file".format(filename)
    AscError = "Unable to parse file '{0}' as .asc file".format(filename)

    f = open(filename)
    lines = f.readlines()
    entries = None 
    pr = ParseResult()
    try :
        entries = extractCsvLog(lines)
    except ValueError as e:
        #print e
        pr.appendError((CsvError, e))
    if entries:
        pr.setEntries(entries)
        return pr
    try :
        entries = extractAscLog(lines)
        pr.setEntries(entries)
        if not entries:
            raise RuntimeError("No usable data found")
    except Exception as e:
        pr.appendError((AscError, e))
    return pr
