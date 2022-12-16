#!/usr/bin/env python

##
# \file parseeyefile.py
# Contains functions to load eyefiles from disk.
#
# \package log
#

import sys
from .eyelog import LogEntry, GazeEntry, SaccadeEntry, FixationEntry
from .eyelog import MessageEntry

import gui.statusmessage as sm


##
# Turns a list of words into a LogEntry
#
# @param splitline a list of the words of one single line in a log file of the
# csv format
#
# \return LogEntry
def getLogEntry(splitline):
    n = int(splitline[0])
    line = splitline
    entry = None

    if n == LogEntry.LGAZE or n == LogEntry.RGAZE:
        if len(splitline) != 5:
            raise ValueError("Gaze entry must contain 5 columns")
        entry = GazeEntry(int(line[0]),
                          float(line[1]),
                          float(line[2]),
                          float(line[3]),
                          float(line[4])
                          )
    elif n == LogEntry.LFIX or n == LogEntry.RFIX:
        if len(splitline) != 5:
            raise ValueError("Fixation entry must contain 5 columns")
        e, eyetime, x, y, dur = \
            int(line[0]),\
            float(line[1]),\
            float(line[2]),\
            float(line[3]),\
            float(line[4])

        entry = FixationEntry(e, eyetime, dur, x, y)
    elif n == LogEntry.LSAC or n == LogEntry.RSAC:
        if len(splitline) != 6:
            raise ValueError("SaccadeEntry must contain 6 columns")
        e, eyetime, x1, y1, x2, y2, dur = \
            int(line[0]), \
            float(line[1]), \
            float(line[2]), \
            float(line[3]), \
            float(line[4]), \
            float(line[5])
        entry = SaccadeEntry(e, eyetime, dur, x1, y1, x2, y2)
    elif n == LogEntry.STIMULUS:
        # FIXME
        raise RuntimeError("Implement the stimulus log entry")
    elif n == LogEntry.MESSAGE:
        if len(splitline) != 3:
            raise ValueError(
                "A message entry should contain an {} a timestamp and "
                "a message".format(LogEntry.MESSAGE)
            )
        # insert tabs back beyond line[3] and strip end of line chars
        stripped_string = "\t".join(line[2:]).strip("\r\n")
        entry = MessageEntry(float(line[1]),
                             stripped_string
                             )
    else:
        raise ValueError(
            "Line: \"" + LogEntry.SEP.join(splitline) + "\" is invalid"
        )
    return entry


##
# read a CsvLog from a list of lines of a csv file.
#
# \return a list of all the log entries of the lines
#
def extractCsvLog(lines):
    logentries = []
    n = 1  # use this to mark location in file where the error is found
    for i in lines:
        try:
            splitline = i.split(LogEntry.SEP)
            logentries.append(getLogEntry(splitline))
        except Exception as e:
            raise ValueError(
                "unable to parse line {1}: \"{0}\"".format(i, n) + str(e)
            )
        n += 1
    return logentries


##
# Read the lines of a EyelinkAscii format.
# @param a list of lines in a Eyelink asc format.
# \return a list of log entries.
#
def extractAscLog(lines):
    '''Examines each line to check whether it has got valid input
       if so it appends it to the log entries. Lines that ain't
       recognized are silently ignored.
    '''
    logentries = []
    MSG = "MSG"
    START = "START"
    END = "END"
    ESACC = "ESACC"
    EFIX = "EFIX"
    SAMPLE = "SAMPLE"  # this is the key for sample parser

    # match a message in the log
    def parse_message(split_line: list, log: list):
        assert split_line[0] == MSG
        if len(split_line):
            split_line = [
                split_line[0], split_line[1], " ".join(split_line[2:])
            ]
        assert len(split_line) == 3 and split_line[0] == MSG
        log.append(MessageEntry(int(split_line[1]), split_line[2].strip()))

    def parse_mono_sample_l(split_line: list, log: list):
        time = float(split_line[0])
        xcoor = float(split_line[1])
        ycoor = float(split_line[2])
        pupsz = float(split_line[3])
        sample = GazeEntry(LogEntry.LGAZE, time, xcoor, ycoor, pupsz)
        log.append(sample)

    def parse_mono_sample_r(split_line: list, log: list):
        time = float(split_line[0])
        xcoor = float(split_line[1])
        ycoor = float(split_line[2])
        pupsz = float(split_line[3])
        sample = GazeEntry(LogEntry.RGAZE, time, xcoor, ycoor, pupsz)
        log.append(sample)

    def parse_binocular_sample(split_line: list, log: list):
        time = float(split_line[0])

        xcoorl = float(split_line[1])
        ycoorl = float(split_line[2])
        pupszl = float(split_line[3])

        xcoorr = float(split_line[4])
        ycoorr = float(split_line[5])
        pupszr = float(split_line[6])

        samplel = GazeEntry(LogEntry.LGAZE, time, xcoorl, ycoorl, pupszl)
        sampler = GazeEntry(LogEntry.RGAZE, time, xcoorr, ycoorr, pupszr)
        log.append(samplel)
        log.append(sampler)

    def parse_fix(split_line: list, log: list):
        eye = split_line[1]
        time_start = int(split_line[2])
        # time_end = int(split_line[3])
        dur = int(split_line[4])
        xcoor = float(split_line[5])
        ycoor = float(split_line[6])
        fix = None
        if eye == "L":
            fix = FixationEntry(LogEntry.LFIX, time_start, dur, xcoor, ycoor)
        elif eye == "R":
            fix = FixationEntry(LogEntry.RFIX, time_start, dur, xcoor, ycoor)

        if fix:
            log.append(fix)

    def parse_saccade(split_line: list, log: list):
        eye = split_line[1]
        time_start = int(split_line[2])
        # time_end = int(split_line[3])
        dur = int(split_line[4])
        xstart = float(split_line[5])
        ystart = float(split_line[6])
        xend = float(split_line[5])
        yend = float(split_line[6])
        sac = None
        if eye == "L":
            sac = SaccadeEntry(
                LogEntry.RSAC, time_start, dur, xstart, ystart, xend, yend
            )
        elif eye == "R":
            sac = SaccadeEntry(
                LogEntry.LSAC, time_start, dur, xstart, ystart, xend, yend
            )
        if sac:
            log.append(sac)

    parsers = {
        MSG: parse_message,
        EFIX: parse_fix,
        ESACC: parse_saccade,
    }

    def parse_start(split_line, _log):
        '''parses start message and installs a sample parser'''
        LEFT = "LEFT"
        RIGHT = "RIGHT"
        coleye1 = split_line[2]
        coleye2 = split_line[3]
        if coleye1 == LEFT and coleye2 == RIGHT:
            parsers[SAMPLE] = parse_binocular_sample
        elif coleye1 == LEFT:
            parsers[SAMPLE] = parse_mono_sample_l
        elif coleye1 == RIGHT:
            parsers[SAMPLE] = parse_mono_sample_r

    def parse_end(split_line, _log):
        '''parses end messeage and removes a sample parser'''
        parsers.pop(SAMPLE, None)

    parsers[START] = parse_start
    parsers[END] = parse_end
    # messages starting with the following keys are ignored
    ignore_keys = set([
        "SFIX",
        "SSACC",
        "SAMPLES",
        "EVENTS",
        "**",
        "PRESCALER",
        "VPRESCALER",
        "PUPIL",
    ])

    # iterate over all lines and add relevant lines to the log
    for index, line in enumerate(lines):
        split_line = line.split()
        try:
            if split_line == []:  # skip empty lines
                continue
            # when a line starts with a integer it should be a sample
            _ = int(split_line[0])
            try:
                if SAMPLE in parsers:
                    parsers[SAMPLE](split_line, logentries)
                    continue
                else:
                    continue
            except Exception as e:
                err = 'Unrecognized sample at line {}:\n\t"{}"\nexception = {}'
                print(err.format(index + 1, line, str(e)), file=sys.stderr)
        except ValueError:
            # It's not a sample, skip it.
            pass

        key = split_line[0]
        if key in parsers:
            parsers[key](split_line, logentries)
        else:
            if key not in ignore_keys:
                print('Unrecognized line {}:\n\t"{}"'.format(
                    index + 1,
                    line),
                    file=sys.stderr
                )
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
    # list of tuples of (string, StatusMessage.OK or StatusMessage.error
    # or StatusMessage.warning)
    def setErrors(self, errorlist):
        self.errors = errorlist

    ##
    # appendErrors(to the list)
    def appendError(self, error):
        self.errors.append(error)

    ##
    # getErrors should be called when the entries are empty
    def getErrors(self):
        return self.errors


##
# \brief Parses the filename
#
# This function first checks whether the file is a valid CsvFile as defined by
# iSpector if this fails it tries to read the file as an Eyelink ascii format
# if this fails it will add Parse errors to the parse result, otherwise it will
# add a list of LogEntry to the ParseResult.
# \returns ParseResult
def parseEyeFile(filename):
    CsvError = "Unable to parse file '{0}' as .csv file".format(filename)
    AscError = "Unable to parse file '{0}' as .asc file".format(filename)

    f = open(filename)
    lines = f.readlines()
    entries = None
    pr = ParseResult()
    try:
        entries = extractCsvLog(lines)
    except ValueError as e:
        pr.appendError((CsvError, e, sm.StatusMessage.warning))
    if entries:
        pr.setEntries(entries)
        return pr
    try:
        entries = extractAscLog(lines)
        pr.setEntries(entries)
        if not entries:
            raise RuntimeError("No usable data found")
    except ValueError as e:
        pr.appendError((AscError, e, sm.StatusMessage.warning))
        pr.appendError(("Unable to parse: ",
                        filename, sm.StatusMessage.error))
    return pr
