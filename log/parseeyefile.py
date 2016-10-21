#!/usr/bin/env python

##
# \file parseeyefile.py
# Contains functions to load eyefiles from disk.
#
# \package log
#

import re
from eyelog import *
import gui.statusmessage as sm 

##
# Turns a list of words into a LogEntry
#
# @param splitline a list of the words of one single line in a logfile of the
# csv format
#
# \return LogEntry
def getLogEntry(splitline):
    n = int(splitline[0])
    l = splitline
    entry = None

    if n == LogEntry.LGAZE or n == LogEntry.RGAZE:
        entry = GazeEntry(int(l[0]),
                          float(l[1]),
                          float(l[2]),
                          float(l[3]),
                          float(l[4])
                          )
    elif n == LogEntry.LFIX or n == LogEntry.RFIX:
        e, eyetime, x, y, dur = int(l[0]),\
                                float(l[1]),\
                                float(l[2]),\
                                float(l[3]),\
                                float(l[4])

        entry = FixationEntry(e, eyetime, dur, x, y)
    
    elif n == LogEntry.STIMULUS:
        #FIXME
        raise RuntimeError("Implement the stimulus log entry")
    elif n == LogEntry.MESSAGE:
        #insert tabs back beyond l[3] and strip end of line chars
        stripped_string = "\t".join(l[2:]).strip("\r\n")
        entry = MessageEntry(float(l[1]),
                             stripped_string
                             )
    else:
        raise ValueError("Line: \"" + LogEntry.SEPARATOR.join(splitline) +
                                      "\" is invalid")
    return entry

##
# read a CsvLog from a list of lines of a csv file.
#
# \return a list of all the logentries of the lines
#
def extractCsvLog(lines):
    logentries = []
    n = 1 # use this to mark location in file where the error is found
    for i in lines:
        try:
            splitline = i.split(LogEntry.SEP);
            logentries.append(getLogEntry(splitline))
        except Exception as e:
            raise ValueError(
                    "unable to parse line {1}: \"{0}\"".format(i, n) + str(e)
                    )
        n+=1
    return logentries

##
# Read the lines of a EyelinkAscii format.
# @param a list of lines in a Eyelink asc format.
# \return a list of logentries.
#
def extractAscLog(lines):
    '''
        Examines each line to check whether it has got valid input
        if so it appends it to the log entries
    '''
    logentries = []
    # asclog has no mention of time in zep or the program
    #float between captured in regex group
    cflt = r"([-+]?[0-9]*\.?[0-9]+)"
    # match a message in the log
    msgre = re.compile(r"MSG\s+(\d+)\s+([^\r\n]*)")
    duosample = re.compile(
        r"^(\d+)\s+" + cflt + r"\s+" + cflt + r"\s+" + cflt + r"\s+" + cflt + r"\s+" + cflt + r"\s+" + cflt + r".+$"
        )
    #monosample would also match a duo sample(sample with both eyes, where the first three columns are assumed to be the left eye and the 2nd three columns belong to the right eye
    monosample = re.compile(r"^(\d+)\s+" + cflt + r"\s+" + cflt + r"\s+" + cflt + r".+$")
    #matches a end fixation, start fixations are ignored
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
            e  = MessageEntry(float(m.group(1)), m.group(2))
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
                lgaze = GazeEntry(LogEntry.LGAZE, eyetime, lx, ly, lp)
                rgaze = GazeEntry(LogEntry.RGAZE, eyetime, rx, ry, rp)
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
                gaze = GazeEntry(LogEntry.LGAZE, eyetime, lx, ly, lp)
            else:
                gaze = GazeEntry(LogEntry.RGAZE, eyetime, lx, ly, lp)
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
                fixentry = FixationEntry(LogEntry.RFIX, fixstart, duration, x, y)
            elif (eyetype == "L"):
                fixentry = FixationEntry(LogEntry.LFIX, fixstart, duration, x, y)
            else:
                raise ValueError("Invalid fixation end: " + i)
            logentries.append(fixentry)
            continue
    return logentries


##
# Result of parsing a eyemovement file.
#
# There can be many problems with parsing a file
# This class returns the files or error that have
# occured
#
class ParseResult:

    ##
    # initialize a empty parseresult
    def __init__(self, entries=[], errors=[]):
        ## a list of LogEntry
        self.entries = entries
        ## a list of errors
        self.errors = errors

    ##
    # after parsing one can add entries with this function
    def setEntries(self, entries):
        self.entries = entries

    ##
    # returns a list of LogEntry or possibly an empty list.
    def getEntries(self):
        return self.entries

    ##
    # Set a list of errors to the error list.
    # list of tuples of (string, StatusMessage.OK or StatusMessage.error or StatusMessage.warning)
    def setErrors(self, errorlist):
        self.errorlist
    
    ##
    # appendErrors(to the list)
    def appendError(self, error):
        self.errors.append(error)
    
    ##
    # getErrors should be called when the entries are empty
    def getErrors(self):
        return self.errors

##\brief Parses the filename
#
# This function first checks whether the file is a valid CsvFile as defined by iSpector
# if this fails it tries to read the file as an Eyelink ascii format if this fails
# it will add Parse errors to the parse result, otherwise it will add a list of LogEntry
# to the ParseResult.
# \returns ParseResult
def parseEyeFile(filename):
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
        pr.appendError((CsvError, e, sm.StatusMessage.warning))
    if entries:
        pr.setEntries(entries)
        return pr
    try :
        entries = extractAscLog(lines)
        pr.setEntries(entries)
        if not entries:
            raise RuntimeError("No usable data found")
    except Exception as e:
        pr.appendError((AscError, e, sm.StatusMessage.warning))
        pr.appendError(("Unable to parse: ",
                filename, sm.StatusMessage.error))
    return pr
